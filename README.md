# tableau_and_smartsheet_extractor
 Dashboard Extractor

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

Edit `.env`:
```
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql+asyncpg://scottsmith@localhost:5432/extractor
```

## Extract

```bash
source .venv/bin/activate
python open_ai_api.py cbps                   # Smartsheet dashboard
python open_ai_api.py cbcbt                  # Tableau (latest report)
python open_ai_api.py cbcbt "Dec 31 2025"   # Tableau (specific report)
```

Output goes to `images/` (screenshots) and `output/YYYY-MM-DD/` (JSON and CSV).

## Upload to DB

**Manually:**
```bash
python db_upload.py cbps  output/YYYY-MM-DD/cbps_dashboard.json
python db_upload.py cbcbt output/YYYY-MM-DD/crosstab.csv
```

Tables are created automatically on first run.

**Automatically after extract** — uncomment these lines in `open_ai_api.py`:
```python
# from db_upload import upload_cbps; await upload_cbps(data)   # in get_cbps_data()
# from db_upload import upload_cbcbt; await upload_cbcbt(data) # in get_cbcbt_data()
```