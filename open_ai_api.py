import asyncio
import json
import os
import csv
from datetime import date
from pathlib import Path
from openai import OpenAI  # pyright: ignore[reportMissingImports]
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
from cbps_schema import CBPS_SCHEMA
from cbcbt_schema import CBCBT_SCHEMA
from web_automator import WebAutomator

load_dotenv()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SMARTSHEET_URL = os.environ["SMARTSHEET_PUBLISH_URL"]
TABLEAU_INDEX_URL = os.environ["TABLEAU_INDEX_URL"]


def _output_dir() -> Path:
    d = Path("output") / date.today().isoformat()
    d.mkdir(parents=True, exist_ok=True)
    return d


def _images_dir() -> Path:
    d = Path("images")
    d.mkdir(exist_ok=True)
    return d


def _upload_image(path: str) -> str:
    f = client.files.create(file=open(path, "rb"), purpose="vision")
    return f.id


def _write_csv(path: Path, rows: list[dict]):
    cols: list[str] = []
    seen: set[str] = set()
    for r in rows:
        for k in r:
            if k not in seen:
                seen.add(k)
                cols.append(k)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


async def get_cbps_data() -> dict:
    automator = WebAutomator()
    image_path = _images_dir() / "smartsheet_dashboard.png"
    await automator.screenshot_smartsheet(SMARTSHEET_URL, str(image_path))

    resp = client.responses.create(
        model="gpt-4o",
        temperature=0,
        instructions=(
            "Extract metrics from the dashboard screenshot. "
            "Only use values visible in the image. "
            "Convert comma-separated numbers to integers. "
            "If unclear/missing, use null. "
            "For activity types, use exact on-screen text in 'label'."
        ),
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Return JSON matching the schema."},
                    {"type": "input_image", "file_id": _upload_image(str(image_path)), "detail": "high"},
                ],
            }
        ],
        text={"format": {"type": "json_schema", **CBPS_SCHEMA}},
    )
    data = json.loads(resp.output_text)
    out = _output_dir() / "cbps_dashboard.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved → {out}")
    # from db_upload import upload_cbps; await upload_cbps(data)
    return data


async def get_cbcbt_data(report_title: str | None = None) -> dict:
    automator = WebAutomator()
    links = await automator.get_tableau_report_links(TABLEAU_INDEX_URL)

    if report_title:
        match = next((l for l in links if report_title.lower() in l["Title"].lower()), None)
        if not match:
            raise ValueError(f"No report matching '{report_title}'. Available: {[l['Title'] for l in links]}")
        link = match
    else:
        link = links[0]

    title_slug = link["Title"].replace(" ", "_")
    image_path = _images_dir() / f"{title_slug}.png"
    await automator.screenshot_tableau(link["URL"], str(image_path))

    resp = client.responses.create(
        model="gpt-4o",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Extract ONLY the two tables: 'Crosstab' and 'Covered Building Count By Tiers'. "
                            "Only use values visible in the image. Convert comma-separated numbers to integers. "
                            "If unclear/missing, use null."
                        ),
                    },
                    {"type": "input_image", "file_id": _upload_image(str(image_path)), "detail": "high"},
                ],
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "cbcbt_table_extract",
                "strict": True,
                "schema": CBCBT_SCHEMA,
            }
        },
    )
    data = json.loads(resp.output_text)
    out_dir = _output_dir()
    crosstab_path = out_dir / "crosstab.csv"
    tiers_path = out_dir / "covered_building_count_by_tiers.csv"
    _write_csv(crosstab_path, data["crosstab"])
    _write_csv(tiers_path, data["covered_building_count_by_tiers"])
    print(f"Saved → {crosstab_path}")
    print(f"Saved → {tiers_path}")
    # from db_upload import upload_cbcbt; await upload_cbcbt(data)
    return data


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2 or sys.argv[1] not in ("cbps", "cbcbt"):
        print("Usage:")
        print("  python open_ai_api.py cbps                    # Smartsheet → output/YYYY-MM-DD/cbps_dashboard.json")
        print("  python open_ai_api.py cbcbt [report title]    # Tableau → output/YYYY-MM-DD/crosstab.csv + covered_building_count_by_tiers.csv")
        sys.exit(1)

    mode = sys.argv[1]
    if mode == "cbps":
        data = asyncio.run(get_cbps_data())
    else:
        title = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
        data = asyncio.run(get_cbcbt_data(title))

    print(json.dumps(data, indent=2))
