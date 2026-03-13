# Implementation Plan: Unified Property Analyzer

**Branch**: `001-unified-property-analyzer` | **Date**: 2026-03-04 | **Spec**: [spec.md](./spec.md)

## Summary

Consolidate the separate Streamlit calculator (app.py) and FastAPI parser (server.py + frontend/) into a single FastAPI application serving an HTMX-powered UI. Replace n8n with direct Google Sheets integration via gspread. Add 6 new investment metrics, a verdict engine, light/dark mode, and responsive mobile layout. All work follows TDD with MCP breadcrumb-guided implementation.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, HTMX (v2.0.4 CDN), Jinja2, gspread, DaisyUI/Tailwind (CDN), Playwright
**Storage**: Google Sheets via gspread service account (Spreadsheet ID: `1dVf1UShQry4nDvM3HbqM9ts0ltbKnruEDKd6lZ_xAMg`)
**Testing**: pytest + pytest-asyncio (unit/integration), Playwright (E2E)
**Linting**: ruff (Python), djlint (Jinja2/HTML templates)
**Target Platform**: Azure App Service (B1, Linux), mobile browsers (iOS Safari, Chrome)
**Project Type**: Web application (monolith — single FastAPI process serving UI + API)
**Performance Goals**: <100ms partial swap latency, <60s paste-to-verdict, <3s portfolio save
**Constraints**: No React/npm build step, no Streamlit, no n8n, CDN-loaded frontend deps
**Scale/Scope**: 2-5 users, 235+ properties in Google Sheet, single Azure instance

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Single-Page | ✅ Pass | HTMX tabs + side-by-side panels, one page for all flows |
| II. No Full-Page Refresh | ✅ Pass | HTMX partial swaps, `hx-target` for results only |
| III. Financial Accuracy | ✅ Pass | Python `Decimal`, Excel-validated formulas, 7 metrics |
| IV. Design System | ✅ Pass | Mockup CSS → Jinja2 templates, both themes via CSS vars |
| V. Parser Integrity | ✅ Pass | Existing 7-step pipeline preserved, SSE via `hx-ext="sse"` |
| VI. TDD | ✅ Pass | Every task starts with failing tests per constitution |

## Project Structure

### Documentation (this feature)

```text
specs/001-unified-property-analyzer/
├── spec.md              # Feature specification (done)
├── research.md          # Phase 0 research (done)
├── data-model.md        # Entity definitions (done)
├── plan.md              # This file
├── contracts/           # API contracts
│   ├── calculate.md
│   ├── parse.md
│   └── sheets.md
└── tasks.md             # Task breakdown (next step)
```

### Source Code (repository root)

```text
property-calculator/
├── server.py                    # FastAPI app entry (existing — extend)
├── backend/
│   ├── config.py                # Settings (existing — extend with Sheets)
│   ├── data/
│   │   ├── states.py            # Tax/insurance rates (NEW)
│   │   └── thresholds.py        # Metric thresholds for verdict (NEW)
│   ├── routes/
│   │   ├── health.py            # (existing)
│   │   ├── parse.py             # SSE parser endpoint (existing)
│   │   ├── pages.py             # Full page renders (NEW)
│   │   ├── calculator.py        # POST /calculate → HTML partial (NEW)
│   │   └── sheets.py            # Google Sheets R/W endpoints (NEW)
│   ├── services/
│   │   ├── parser.py            # 7-step pipeline (existing)
│   │   ├── openai_client.py     # Azure OpenAI (existing)
│   │   ├── rentcast.py          # Rent API (existing)
│   │   ├── web_search.py        # URL search (existing)
│   │   ├── page_scraper.py      # Playwright scrape (existing)
│   │   ├── calculator.py        # All calc formulas (NEW — from app.py)
│   │   ├── verdict.py           # INVEST/REVIEW/PASS engine (NEW)
│   │   └── sheets.py            # gspread service (NEW)
│   └── schemas/
│       ├── property.py          # 15-field model (existing)
│       └── calculator.py        # CalculatorInput + Result models (NEW)
├── templates/
│   ├── base.html                # Layout: head, nav, HTMX/DaisyUI CDN (NEW)
│   ├── index.html               # Main page — chat + calc panels (NEW)
│   └── partials/
│       ├── chat_bubble.html     # User/system message bubbles (NEW)
│       ├── pipeline_steps.html  # Collapsible 7-step progress (NEW)
│       ├── extracted_data.html  # Parsed property bullet points (NEW)
│       ├── sidebar_commercial.html  # Commercial input form (NEW)
│       ├── sidebar_residential.html # Residential input form (NEW)
│       ├── results_overview.html    # Verdict + metrics + tables (NEW)
│       ├── portfolio_table.html     # Google Sheet data grid (NEW)
│       └── compare_columns.html     # Side-by-side deal comparison (NEW)
├── static/
│   ├── css/
│   │   └── theme.css            # CSS variables for dark/light (NEW)
│   ├── js/
│   │   ├── parse.js             # SSE consumption + form population (NEW)
│   │   └── theme.js             # Dark/light toggle persistence (NEW)
│   └── favicon.png              # (existing)
├── tests/
│   ├── unit/
│   │   ├── test_calculator.py   # Calculator formulas vs Excel (NEW)
│   │   ├── test_verdict.py      # Verdict engine boundary tests (NEW)
│   │   └── test_states.py       # State data correctness (NEW)
│   ├── integration/
│   │   ├── test_routes.py       # HTMX endpoint response tests (NEW)
│   │   └── test_sheets.py       # Google Sheets R/W tests (NEW)
│   └── e2e/
│       └── test_full_flow.py    # Playwright browser tests (NEW)
├── pyproject.toml               # ruff + djlint config (NEW)
├── requirements.txt             # Pinned versions (UPDATE)
└── .env.example                 # Add GOOGLE_SERVICE_ACCOUNT (UPDATE)
```

**Structure Decision**: Single FastAPI process serves both API (existing `/api/` routes) and UI (new Jinja2 templates). No separate frontend build. HTMX + DaisyUI loaded via CDN `<script>` tags.

## API Contracts

### POST /calculate
- **Input**: Form data (all calculator inputs as `name=value` pairs)
- **Output**: HTML partial (`partials/results_overview.html`)
- **HTMX**: `hx-push-url="true"` updates browser URL with all params
- **Latency target**: <100ms

### POST /api/parse
- **Input**: JSON `{"text": "..."}`
- **Output**: SSE stream with events: `step` (7× progress), `complete` (final JSON)
- **Existing endpoint** — no changes to API contract, only UI consumption changes

### GET /api/properties
- **Input**: None (optional query params for filtering)
- **Output**: JSON array of portfolio entries from Google Sheet
- **Source**: gspread `get_all_records()` on sheet `PropertiesForSale`

### POST /api/properties
- **Input**: JSON with 21 fields (15 parsed + 6 calculated)
- **Output**: JSON `{"status": "saved", "row": N}`
- **Target**: gspread `append_rows()` to sheet `PropertiesForSale`

### GET /tab/{name}
- **Input**: Tab name (`analyze`, `portfolio`, `compare`)
- **Output**: HTML partial for the requested tab content
- **HTMX**: Lazy-loaded tabs, only active tab content fetched

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Small JS files (parse.js, theme.js) | SSE consumption requires EventSource API; theme toggle needs localStorage | HTMX SSE ext handles display but not form auto-population from parsed JSON; pure server-side theme toggle would flash on load |
| CSS variables for dual themes | Light/dark mode requirement from constitution | Single theme would be simpler but user explicitly requested both |
