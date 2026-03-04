# Quickstart: Property Analyzer Development

## Prerequisites
- Python 3.11+
- Google Cloud service account JSON key with Sheets API enabled
- Azure OpenAI API key (for parser)
- Rentcast API key (for projected rents)

## Setup

```bash
# 1. Clone and branch
git clone https://github.com/vyente-ruffin/property-calculator.git
cd property-calculator
git checkout 001-unified-property-analyzer

# 2. Virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers (for scraping + E2E tests)
playwright install chromium

# 5. Configure environment
cp .env.example .env
# Edit .env with:
#   RENTCAST_API_KEY=...
#   AZURE_OPENAI_API_KEY=...
#   AZURE_OPENAI_ENDPOINT=...
#   AZURE_OPENAI_DEPLOYMENT=gpt-4o
#   GOOGLE_SERVICE_ACCOUNT={"type":"service_account","project_id":"..."}
#   GOOGLE_SHEET_ID=1dVf1UShQry4nDvM3HbqM9ts0ltbKnruEDKd6lZ_xAMg

# 6. Share Google Sheet with service account email
# Go to the Google Sheet → Share → add the service account email as Editor
```

## Run

```bash
# Development server
uvicorn server:app --host 0.0.0.0 --port 8090 --reload

# Open browser
open http://localhost:8090
```

## Test

```bash
# Lint first
ruff check .
djlint templates/

# Unit tests
pytest tests/unit/ -v

# Integration tests (requires .env)
pytest tests/integration/ -v

# E2E tests (requires running server)
pytest tests/e2e/ -v
```

## Key Commands for AI Agents

When implementing tasks, use these MCP queries to ground work in authoritative docs:

```
📚 Context7: "/bigskysoftware/htmx" → "hx-post hx-trigger hx-target partial swap"
📚 Context7: "/burnash/gspread" → "service account from dict append rows get all records"
📚 Context7: "/websites/fastapi_tiangolo" → "Jinja2Templates TemplateResponse static files"
📚 Context7: "/websites/fastapi_tiangolo" → "StreamingResponse SSE text/event-stream"
📚 mslearn: "Azure App Service Python FastAPI deployment"
```
