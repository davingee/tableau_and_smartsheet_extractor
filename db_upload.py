import asyncio
import json
import os
from datetime import date
from pathlib import Path
import asyncpg  # pyright: ignore[reportMissingImports]
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]

load_dotenv()

# Strip the SQLAlchemy driver prefix — asyncpg uses raw postgres:// URLs
DATABASE_URL = os.environ["DATABASE_URL"].replace("postgresql+asyncpg://", "postgresql://")


async def _connect():
    return await asyncpg.connect(DATABASE_URL)


async def setup_tables(conn):
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS cbps_dashboard (
            id              SERIAL PRIMARY KEY,
            extracted_date  DATE NOT NULL,
            title           TEXT,
            applications_to_date            INTEGER,
            compliance_approved_or_pre_approved INTEGER,
            compliance_pending              INTEGER,
            compliance_withdrawn            INTEGER,
            compliance_denied               INTEGER,
            tier1_approved_or_pre_approved  INTEGER,
            tier1_pending                   INTEGER,
            tier1_withdrawn                 INTEGER,
            tier1_denied                    INTEGER,
            tier2_approved                  INTEGER,
            tier2_pending                   INTEGER,
            tier2_withdrawn                 INTEGER,
            tier2_denied                    INTEGER,
            total_application_gfa           BIGINT,
            approved_gfa                    BIGINT,
            compliance_count                INTEGER,
            exemption_count                 INTEGER,
            building_tier1_count            INTEGER,
            building_tier2_count            INTEGER
        )
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS cbps_activity_types (
            id              SERIAL PRIMARY KEY,
            extracted_date  DATE NOT NULL,
            label           TEXT,
            percent         INTEGER,
            count           INTEGER
        )
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS cbps_cumulative_applications (
            id              SERIAL PRIMARY KEY,
            extracted_date  DATE NOT NULL,
            period          TEXT,
            applications    INTEGER
        )
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS crosstab (
            id              SERIAL PRIMARY KEY,
            extracted_date  DATE NOT NULL,
            county          TEXT,
            building_count  INTEGER,
            owner_count     INTEGER,
            parcel_count    INTEGER
        )
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS covered_building_count_by_tiers (
            id                          SERIAL PRIMARY KEY,
            extracted_date              DATE NOT NULL,
            county                      TEXT,
            grand_total                 INTEGER,
            tier1_over_220k             INTEGER,
            tier1_50k_90k               INTEGER,
            tier1_90k_220k              INTEGER,
            tier1_total                 INTEGER,
            tier2_condos                INTEGER,
            tier2_mf_5_plus             INTEGER,
            tier2_other_residential     INTEGER,
            tier2_20k_50k               INTEGER,
            tier2_total                 INTEGER
        )
    """)


async def upload_cbps(data: dict, extracted_date: date | None = None):
    extracted_date = extracted_date or date.today()
    conn = await _connect()
    try:
        await setup_tables(conn)

        d = data
        s = d["overview_by_status"]
        comp = s["compliance_and_exemption_applications"]
        t1 = s["tier_1"]
        t2 = s["tier_2"]

        # Merge percent and count arrays by label
        percents = {x["label"]: x["percent"] for x in d["overview_by_building_activity_type"]["portion_of_applications_percent"]}
        counts = {x["label"]: x["count"] for x in d["overview_by_building_activity_type"]["activity_type_counts"]}

        await conn.execute("""
            INSERT INTO cbps_dashboard (
                extracted_date, title, applications_to_date,
                compliance_approved_or_pre_approved, compliance_pending, compliance_withdrawn, compliance_denied,
                tier1_approved_or_pre_approved, tier1_pending, tier1_withdrawn, tier1_denied,
                tier2_approved, tier2_pending, tier2_withdrawn, tier2_denied,
                total_application_gfa, approved_gfa,
                compliance_count, exemption_count,
                building_tier1_count, building_tier2_count
            ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21)
        """,
            extracted_date,
            d["dashboard"]["title"],
            d["dashboard"]["applications_to_date"],
            comp["approved_or_pre_approved"], comp["pending"], comp["withdrawn"], comp["denied"],
            t1["approved_or_pre_approved"], t1["pending"], t1["withdrawn"], t1["denied"],
            t2["approved"], t2["pending"], t2["withdrawn"], t2["denied"],
            d["gross_floor_area_sq_ft"]["total_application_gfa"],
            d["gross_floor_area_sq_ft"]["approved_gfa"],
            d["overview_by_application_type"]["counts"]["compliance"],
            d["overview_by_application_type"]["counts"]["exemption"],
            d["building_tier"]["counts"]["tier_1"],
            d["building_tier"]["counts"]["tier_2"],
        )

        all_labels = sorted(set(percents) | set(counts))
        for label in all_labels:
            await conn.execute("""
                INSERT INTO cbps_activity_types (extracted_date, label, percent, count)
                VALUES ($1, $2, $3, $4)
            """, extracted_date, label, percents.get(label), counts.get(label))

        for row in d["cumulative_applications"]:
            await conn.execute("""
                INSERT INTO cbps_cumulative_applications (extracted_date, period, applications)
                VALUES ($1, $2, $3)
            """, extracted_date, row["period"], row["applications"])

        print(f"Uploaded cbps_dashboard for {extracted_date}")
    finally:
        await conn.close()


async def upload_cbcbt(data: dict, extracted_date: date | None = None):
    extracted_date = extracted_date or date.today()
    conn = await _connect()
    try:
        await setup_tables(conn)

        for row in data["crosstab"]:
            await conn.execute("""
                INSERT INTO crosstab (extracted_date, county, building_count, owner_count, parcel_count)
                VALUES ($1, $2, $3, $4, $5)
            """, extracted_date, row["County"], row["Building Count"], row["Owner Count"], row["Parcel Count"])

        for row in data["covered_building_count_by_tiers"]:
            await conn.execute("""
                INSERT INTO covered_building_count_by_tiers (
                    extracted_date, county, grand_total,
                    tier1_over_220k, tier1_50k_90k, tier1_90k_220k, tier1_total,
                    tier2_condos, tier2_mf_5_plus, tier2_other_residential, tier2_20k_50k, tier2_total
                ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)
            """,
                extracted_date,
                row["County"],
                row["Grand Total"],
                row["Tier1 >220K"],
                row["Tier1 >50K-90K"],
                row["Tier1 >90K-220K"],
                row["Tier1 Total"],
                row["Tier2 >20K Condos"],
                row["Tier2 >20K MF (5+)"],
                row["Tier2 >20K Other Residential"],
                row["Tier2 >20K-50K"],
                row["Tier2 Total"],
            )

        print(f"Uploaded cbcbt tables for {extracted_date}")
    finally:
        await conn.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3 or sys.argv[1] not in ("cbps", "cbcbt"):
        print("Usage:")
        print("  python db_upload.py cbps  output/YYYY-MM-DD/cbps_dashboard.json")
        print("  python db_upload.py cbcbt output/YYYY-MM-DD/cbps_dashboard.json   # expects crosstab + tiers in same folder")
        sys.exit(1)

    mode, json_path = sys.argv[1], Path(sys.argv[2])

    if mode == "cbps":
        data = json.loads(json_path.read_text())
        asyncio.run(upload_cbps(data))
    else:
        folder = json_path.parent
        data = {
            "crosstab": [],
            "covered_building_count_by_tiers": [],
        }
        import csv
        with open(folder / "crosstab.csv", encoding="utf-8") as f:
            data["crosstab"] = [{k: (int(v) if v else None) if k != "County" else v for k, v in row.items()} for row in csv.DictReader(f)]
        with open(folder / "covered_building_count_by_tiers.csv", encoding="utf-8") as f:
            data["covered_building_count_by_tiers"] = [{k: (int(v) if v else None) if k != "County" else v for k, v in row.items()} for row in csv.DictReader(f)]
        asyncio.run(upload_cbcbt(data))
