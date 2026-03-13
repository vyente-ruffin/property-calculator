# Research Notes: Unified Property Analyzer

**Branch**: `001-unified-property-analyzer` | **Date**: 2026-03-04

## HTMX (Context7: /bigskysoftware/htmx)

### SSE Extension
- `hx-ext="sse"` + `sse-connect="/url"` + `sse-swap="eventName"` for real-time streaming
- Named events: `sse-swap="event1,event2"` for multiple event types
- Trigger HTMX requests on SSE: `hx-trigger="sse:eventName"`
- Child elements can listen independently from the same SSE source

### Partial Swaps
- `hx-post="/calculate"` + `hx-target="#results"` + `hx-trigger="change"` — only target swaps
- `hx-push-url="true"` — updates browser URL bar (shareable state)
- `hx-include="[name]"` — serializes form inputs across the page
- `hx-swap="innerHTML"` (default), `outerHTML`, `beforeend`, etc.

### Key Patterns for This App
```html
<!-- Sidebar input triggers partial results update -->
<input name="purchase_price" hx-post="/calculate" hx-trigger="change" hx-target="#results" hx-include="[name]">

<!-- SSE pipeline progress -->
<div hx-ext="sse" sse-connect="/api/parse-stream">
  <div sse-swap="step"><!-- Each step event replaces this --></div>
  <div sse-swap="complete"><!-- Final result here --></div>
</div>
```

## gspread (Context7: /burnash/gspread)

### Service Account Auth
```python
import gspread, json, os
service_account_info = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT'])
gc = gspread.service_account_from_dict(service_account_info)
```
- Store JSON key as env variable `GOOGLE_SERVICE_ACCOUNT`
- Spreadsheet must be shared with service account email

### Read/Write
```python
sh = gc.open_by_key("1dVf1UShQry4nDvM3HbqM9ts0ltbKnruEDKd6lZ_xAMg")
ws = sh.sheet1
rows = ws.get_all_records()  # List of dicts, header row = keys
ws.append_rows([["$1,970,000", "252 W 11th St", ...]], value_input_option="USER_ENTERED")
```
- `get_all_records()` returns list of dicts (first row = keys)
- `append_rows()` with `value_input_option="USER_ENTERED"` for formula/format preservation

### Sheet ID
- Spreadsheet ID: `1dVf1UShQry4nDvM3HbqM9ts0ltbKnruEDKd6lZ_xAMg`
- Tab: "PropertiesForSale" (gid=0)
- 21 existing columns (A-U), new columns V-AA for calculated metrics

## FastAPI + Jinja2 (Context7: /websites/fastapi_tiangolo)

### Template Setup
```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={...})
```

### Partial HTML for HTMX
```python
@app.post("/calculate", response_class=HTMLResponse)
async def calculate(request: Request):
    form = await request.form()
    results = calculator.run(dict(form))
    return templates.TemplateResponse(request=request, name="partials/results.html", context={"r": results})
```

### SSE Streaming (existing pattern in codebase)
```python
from fastapi.responses import StreamingResponse

@app.post("/api/parse")
async def parse(request: Request):
    body = await request.json()
    return StreamingResponse(
        parser.run_pipeline(body["text"]),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )
```

## Google Sheet Schema

### Existing Columns (A-U) — DO NOT MODIFY
| Col | Header | Fill Rate |
|-----|--------|-----------|
| A | Price | 100% |
| B | Address | 100% |
| C | City | 100% |
| D | Cap Rate | 67% |
| E | Date On Market | 85% |
| F | Monthly Rental Income (Projected) | 98% |
| G | Monthly Rental Income (Actual) | 19% |
| H | Annual Rent Income (Projected) | 97% |
| I | Annual Rent Income (Actual) | 19% |
| J | NOI | 82% |
| K | Lot / building size | 100% |
| L | Total Units | 100% |
| M | Unit Mix Summary | 100% |
| N | Link | 97% |
| O | Description | 100% |
| P | Analyze | 100% (hyperlinks) |
| Q | Investible | 100% (✅ GOOD / ❌ BAD) |
| R | Cashflow | 100% (-$97,866 to +$67,795) |
| S | Notes | 3% (manual) |
| T | Monthly Rental Income | 0% (DEAD) |
| U | Annual Rent Income | 0.4% (DEAD) |

### New Columns (V-AA) — TO BE ADDED
| Col | Header | Source |
|-----|--------|--------|
| V | Cash-on-Cash | Calculator |
| W | DSCR | Calculator |
| X | Price/Unit | Calculator |
| Y | Break-Even Occ | Calculator |
| Z | Verdict | Verdict engine |
| AA | Analyze URL | App URL with query params |

## Dependencies to Pin
```
fastapi==0.115.6
uvicorn[standard]==0.32.1
jinja2==3.1.4
gspread==6.1.4
google-auth==2.36.0
pydantic-settings==2.6.1
openai==1.55.3
httpx==0.27.2
playwright==1.49.1
python-multipart==0.0.17
ruff==0.8.4
djlint==1.36.4
pytest==8.3.4
pytest-asyncio==0.24.0
```
