# Tasks: Unified Property Analyzer

**Input**: Design documents from `/specs/001-unified-property-analyzer/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**TDD**: Every task follows Red-Green-Refactor. Tests written FIRST, must FAIL before implementation.
**MCP Breadcrumbs**: Every task includes a 📚 query the implementing agent MUST run before coding.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1-US6)
- **DoD**: Definition of Done checklist per task

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project scaffolding, tooling, and configuration

- [ ] T001 Create directory structure per plan.md
  - Create: `backend/data/`, `templates/`, `templates/partials/`, `static/css/`, `static/js/`, `tests/unit/`, `tests/integration/`, `tests/e2e/`
  - Create empty `__init__.py` in all Python package dirs
  - 📚 MCP: Context7 query "/websites/fastapi_tiangolo" for "project structure static files templates directory"
  - **DoD**: All directories exist, `server.py` imports succeed, `uvicorn server:app` starts without error

- [ ] T002 Pin dependencies in requirements.txt
  - Replace all `>=` with `==` pinned versions (see research.md for exact versions)
  - Add: `jinja2`, `gspread`, `google-auth`, `python-multipart`, `ruff`, `djlint`, `pytest`, `pytest-asyncio`
  - Remove: `streamlit`, `plotly`, `psutil` (no longer used)
  - Run `pip install -r requirements.txt` in venv to verify
  - 📚 MCP: Context7 query "/burnash/gspread" for "installation requirements dependencies"
  - **DoD**: `pip install -r requirements.txt` succeeds, no `>=` ranges remain, `python -c "import gspread, jinja2"` works

- [ ] T003 [P] Configure linting in pyproject.toml
  - Create `pyproject.toml` with ruff config: `select = ["E", "F", "W", "I", "N", "UP", "B", "A", "C4", "SIM"]`
  - Add djlint config for Jinja2 templates
  - `ruff check .` must pass on existing backend/ code (fix any issues)
  - 📚 MCP: Context7 query "/astral-sh/ruff" for "pyproject.toml configuration select rules"
  - **DoD**: `ruff check .` exits 0, `djlint templates/` exits 0 (or no templates yet = vacuous pass)

- [ ] T004 [P] Configure pytest in pyproject.toml
  - Add `[tool.pytest.ini_options]` with `asyncio_mode = "auto"`, test paths
  - Create `tests/conftest.py` with shared fixtures (FastAPI TestClient, sample property data)
  - `pytest --co` (collect-only) must succeed
  - 📚 MCP: Context7 query "/pytest-dev/pytest" for "pyproject.toml configuration asyncio_mode conftest fixtures"
  - **DoD**: `pytest --co` discovers test files, conftest.py provides `client` and `sample_property` fixtures

- [ ] T005 Update .env.example with new variables
  - Add: `GOOGLE_SERVICE_ACCOUNT={}`, `GOOGLE_SHEET_ID=1dVf1UShQry4nDvM3HbqM9ts0ltbKnruEDKd6lZ_xAMg`
  - Keep existing: `RENTCAST_API_KEY`, `AZURE_OPENAI_*`
  - Update `backend/config.py` to read new env vars via pydantic-settings
  - 📚 MCP: Context7 query "/websites/fastapi_tiangolo" for "pydantic settings environment variables configuration"
  - **DoD**: `config.py` loads `GOOGLE_SERVICE_ACCOUNT` and `GOOGLE_SHEET_ID`, raises clear error if missing

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core services that ALL user stories depend on. No UI work until these pass tests.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T006 Create state data module at `backend/data/states.py`
  - TDD: Write `tests/unit/test_states.py` FIRST
    - Test all 6 states have tax_rate and insurance_rate
    - Test lookup by abbreviation returns correct rates
    - Test unknown state raises ValueError
  - Implement: dict of {state_abbrev: {tax_rate: Decimal, insurance_rate: Decimal}}
  - 📚 MCP: Context7 query "/python/cpython" for "decimal module precision financial calculations"
  - **DoD**: `pytest tests/unit/test_states.py` passes, all 6 states verified, uses Decimal

- [ ] T007 Create metric thresholds at `backend/data/thresholds.py`
  - TDD: Write `tests/unit/test_thresholds.py` FIRST
    - Test each metric returns "green", "yellow", or "red" for boundary values
    - Test Cap Rate: 6.0→green, 5.9→yellow, 3.9→red
    - Test DSCR: 1.25→green, 1.24→yellow, 0.99→red
    - Test CoC: 8.0→green, 7.9→yellow, 3.9→red
    - Test Break-Even: 74→green, 75→yellow, 86→red
  - Implement: `score_metric(name, value) → "green"|"yellow"|"red"`
  - 📚 MCP: Context7 query "/python/cpython" for "decimal comparison operators"
  - **DoD**: `pytest tests/unit/test_thresholds.py` passes, all boundary conditions verified

- [ ] T008 Create calculator service at `backend/services/calculator.py`
  - TDD: Write `tests/unit/test_calculator.py` FIRST — validate against Excel reference values:
    - Commercial test case: Purchase=$1,970,000, Down=30%, Rate=6.5%, Term=25yr, Gross=$152,195, NOI=$106,548, Vacancy=3%, Expenses=$5,000, State=CA → verify: NOI_est=$95,381, Cash Flow=$8,391, CoC=6.2%, DSCR=1.18, Cap Rate=5.4%, monthly_payment=$7,249
    - Residential test case: Purchase=$650,000, Down=20%, Rate=6.5%, Term=15yr, Rent=$5,000, State=CA → verify monthly expenses, 3 occupancy scenarios
    - New metrics: Cap Rate, DSCR, Price/Unit, Break-Even, GRM
    - Edge cases: 0% down, 100% vacancy, 0 units (should raise)
  - Implement: Pure functions using Decimal, NO UI dependencies
  - Functions: `calculate_commercial(input) → CalculationResult`, `calculate_residential(input) → CalculationResult`
  - 📚 MCP: Context7 query "/python/cpython" for "decimal quantize ROUND_HALF_UP financial rounding"
  - **DoD**: `pytest tests/unit/test_calculator.py` passes, ALL values match Excel within ±$1, 7 metrics computed

- [ ] T009 Create verdict engine at `backend/services/verdict.py`
  - TDD: Write `tests/unit/test_verdict.py` FIRST:
    - Test INVEST: all 4 metrics green → verdict="INVEST", 3 reasons, all scores green
    - Test PASS: any metric red → verdict="PASS", reasons explain red metrics
    - Test PASS: DSCR < 1.0 → always PASS regardless of other metrics
    - Test REVIEW: mixed green/yellow, no red → verdict="REVIEW"
    - Test exactly 3 reasons returned for every verdict
  - Implement: `generate_verdict(calc_result) → Verdict` using thresholds from T007
  - 📚 MCP: Context7 query "/python/cpython" for "dataclass frozen immutable"
  - **DoD**: `pytest tests/unit/test_verdict.py` passes, all 3 verdict outcomes tested with boundary values

- [ ] T010 Create calculator Pydantic models at `backend/schemas/calculator.py`
  - TDD: Write `tests/unit/test_schemas.py` FIRST:
    - Test CalculatorInput validates types, enforces ranges (down 0-100, vacancy 0-50)
    - Test CalculatorInput defaults match spec (purchase=1970000, down=30, etc.)
    - Test CalculationResult serializes correctly for template rendering
  - Implement: `CalculatorInput` and `CalculationResult` Pydantic models per data-model.md
  - 📚 MCP: Context7 query "/websites/fastapi_tiangolo" for "pydantic model field validation default values"
  - **DoD**: `pytest tests/unit/test_schemas.py` passes, all validation rules enforced

- [ ] T011 Create Google Sheets service at `backend/services/sheets.py`
  - TDD: Write `tests/integration/test_sheets.py` FIRST (skip if no credentials):
    - Test `get_all_properties()` returns list of dicts with expected column headers
    - Test `append_property(data)` adds a row and returns row number
    - Test handles missing GOOGLE_SERVICE_ACCOUNT gracefully (raises SheetsNotConfigured)
  - Implement: `SheetsService` class with `get_all_properties()`, `append_property(data)`, `get_summary()`
  - Use `gspread.service_account_from_dict(json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT']))`
  - Sheet ID from config, tab "PropertiesForSale"
  - 📚 MCP: Context7 query "/burnash/gspread" for "service_account_from_dict open_by_key get_all_records append_rows"
  - **DoD**: `pytest tests/integration/test_sheets.py` passes (or skips cleanly if no creds), read/write both work

- [ ] T012 Mount Jinja2 templates and static files in server.py
  - TDD: Write `tests/integration/test_routes.py` FIRST:
    - Test GET `/` returns 200 with HTML containing "405 Network"
    - Test GET `/` response includes HTMX and DaisyUI CDN script tags
    - Test static files served at `/static/css/theme.css`
  - Implement: Add `Jinja2Templates`, `StaticFiles` mount, `GET /` route
  - Create minimal `templates/base.html` with HTMX v2.0.4 + DaisyUI CDN + fonts
  - Create minimal `templates/index.html` extending base with placeholder content
  - 📚 MCP: Context7 query "/websites/fastapi_tiangolo" for "Jinja2Templates StaticFiles mount TemplateResponse"
  - **DoD**: `pytest tests/integration/test_routes.py` passes, `http://localhost:8090` shows the page

**Checkpoint**: Foundation ready — calculator works, verdict works, Sheets works, templates render. User story implementation can begin.

---

## Phase 3: User Story 1 — Paste Listing & Get Verdict (Priority: P1) 🎯 MVP

**Goal**: Paste listing text → parse → auto-populate calculator → see verdict with metrics
**Independent Test**: Paste sample listing, verify 15 fields extracted, 7 metrics calculated, verdict displayed

### Tests for User Story 1

> **Write these tests FIRST. They MUST fail before implementation.**

- [ ] T013 [P] [US1] Unit test for parse-to-calculator field mapping in `tests/unit/test_field_mapping.py`
  - Test: parsed PropertyData → CalculatorInput mapping (Price→purchase_price, City→state extraction, etc.)
  - Test: handles missing fields gracefully (null NOI → use default)
  - 📚 MCP: Context7 query "/python/cpython" for "regex extract state abbreviation from string"
  - **DoD**: Tests written and FAIL (no implementation yet)

- [ ] T014 [P] [US1] Integration test for POST /calculate endpoint in `tests/integration/test_calculate.py`
  - Test: POST form data → returns HTML with verdict banner, 4 metric cards, expense table
  - Test: response contains `hx-push-url` or URL params
  - Test: commercial vs residential returns different form structures
  - 📚 MCP: Context7 query "/websites/fastapi_tiangolo" for "TestClient post form data response text"
  - **DoD**: Tests written and FAIL (no endpoint yet)

### Implementation for User Story 1

- [ ] T015 [US1] Create CSS theme system at `static/css/theme.css`
  - Dark theme CSS variables (from mockup.html): midnight, surface, gold, signal colors
  - Light theme CSS variables: parchment (#f8f6f1), white surface, darker gold, adjusted signals
  - `data-theme="dark"` and `data-theme="light"` on `<html>`
  - All component styles using CSS variables only
  - 📚 MCP: Context7 query "/bigskysoftware/htmx" for "CSS class swap theme toggle"
  - **DoD**: Both themes render correctly when toggling `data-theme` attribute manually in devtools

- [ ] T016 [US1] Create theme toggle JS at `static/js/theme.js`
  - Toggle between `data-theme="dark"` and `data-theme="light"`
  - Persist preference in localStorage
  - Load saved preference on page load (no flash of wrong theme)
  - 📚 MCP: Context7 query "/bigskysoftware/htmx" for "hx-on htmx events client side"
  - **DoD**: Click toggle → theme swaps instantly, refresh → preference preserved

- [ ] T017 [US1] Build base.html template at `templates/base.html`
  - Header: 405 Network brand, dark/light toggle, green status dot
  - HTMX v2.0.4 CDN, HTMX SSE extension CDN, DaisyUI CDN, Tailwind CDN (all versioned URLs)
  - Google Fonts: Bricolage Grotesque, JetBrains Mono, Outfit
  - Link to `static/css/theme.css`, `static/js/theme.js`, `static/js/parse.js`
  - `{% block content %}{% endblock %}` for page content
  - 📚 MCP: Context7 query "/bigskysoftware/htmx" for "installation CDN script tag extensions"
  - **DoD**: `djlint templates/base.html` passes, page loads with correct fonts and header

- [ ] T018 [US1] Build index.html with two-panel layout at `templates/index.html`
  - Desktop: chat panel (400px left) + calculator panel (flex right)
  - Mobile: tabbed layout (Parse / Analyze / Saved) via CSS media queries
  - Chat panel: text area + "Parse Listing" button + message container
  - Calculator panel: type toggle + sidebar form + results area
  - Extends base.html
  - 📚 MCP: Context7 query "/bigskysoftware/htmx" for "hx-get hx-target tabs lazy loading"
  - **DoD**: `djlint templates/index.html` passes, two-panel layout visible at desktop width, tabs at mobile width

- [ ] T019 [US1] Build sidebar_commercial.html partial at `templates/partials/sidebar_commercial.html`
  - All commercial inputs with `hx-post="/calculate"` `hx-trigger="change"` `hx-target="#results"` `hx-include="[name]"`
  - Sliders: Down %, Vacancy %, Interest Rate %, Loan Term — with JS value display
  - Number inputs: Purchase Price, Gross Rents, NOI, Expenses, Units
  - Select: State dropdown (AZ, CA, IN, NV, TX, MI)
  - Text: Property URL
  - 📚 MCP: Context7 query "/bigskysoftware/htmx" for "hx-post hx-trigger change hx-include form inputs"
  - **DoD**: Form renders, slider values display, changing any input triggers POST to /calculate

- [ ] T020 [US1] Build sidebar_residential.html partial at `templates/partials/sidebar_residential.html`
  - Residential inputs: Purchase Price, Down %, Rate, Loan Term (15/30), Monthly Rent, State, URL
  - Same HTMX attributes as commercial form
  - 📚 MCP: Context7 query "/bigskysoftware/htmx" for "hx-swap-oob out of band swap"
  - **DoD**: Form renders, switching property type swaps sidebar content

- [ ] T021 [US1] Build results_overview.html partial at `templates/partials/results_overview.html`
  - Verdict banner (INVEST/REVIEW/PASS with 3 reasons, color-coded)
  - 4 primary metric cards (Cap Rate, CoC, DSCR, NOI) with top color bars
  - 3 secondary metric cards (Price/Unit, Break-Even, GRM)
  - NOI comparison (broker vs estimated with delta %)
  - Operating expenses table (monthly + annual)
  - Investment analysis table
  - Investment summary grid
  - All values from `CalculationResult` context variable
  - 📚 MCP: Context7 query "/bigskysoftware/htmx" for "hx-push-url URL state management"
  - **DoD**: Partial renders with sample data, all 7 metrics displayed, colors match thresholds

- [ ] T022 [US1] Create POST /calculate route at `backend/routes/calculator.py`
  - Accept form data, parse into CalculatorInput
  - Call calculator service (T008), then verdict engine (T009)
  - Return rendered `partials/results_overview.html` with context
  - Set `HX-Push-Url` header with all form params for shareable URLs
  - Mount route in server.py
  - 📚 MCP: Context7 query "/websites/fastapi_tiangolo" for "Form data request body TemplateResponse"
  - **DoD**: `pytest tests/integration/test_calculate.py` PASSES, manual test shows results update on input change

- [ ] T023 [US1] Create field mapping util at `backend/services/field_mapper.py`
  - Map parsed PropertyData fields → CalculatorInput fields
  - Extract state abbreviation from "City, ST ZIP" format
  - Handle missing/null fields with sensible defaults
  - 📚 MCP: Context7 query "/python/cpython" for "regex named groups state abbreviation parsing"
  - **DoD**: `pytest tests/unit/test_field_mapping.py` PASSES, all field mappings verified

- [ ] T024 [US1] Build parse.js for SSE consumption at `static/js/parse.js`
  - Fetch POST `/api/parse` with listing text as JSON body
  - Parse SSE stream (ReadableStream line-by-line, same pattern as existing frontend/chat.js)
  - Update pipeline step indicators in chat panel (collapsible)
  - On `complete` event: render extracted data as bullet points in chat
  - Auto-populate calculator form fields from parsed JSON (set input values + trigger HTMX)
  - ~50-80 lines of JS
  - 📚 MCP: Context7 query "/bigskysoftware/htmx" for "htmx trigger event programmatically htmx.trigger"
  - **DoD**: Paste listing → pipeline steps animate → data appears in chat → calculator form fills → results update

- [ ] T025 [US1] Build pipeline_steps.html partial at `templates/partials/pipeline_steps.html`
  - Collapsible container with 7 step rows
  - Each step: icon (⏳/✅/⏭/❌), name, detail text
  - Updated via parse.js DOM manipulation during SSE stream
  - 📚 MCP: Context7 query "/bigskysoftware/htmx" for "sse extension named events swap"
  - **DoD**: Pipeline renders in chat, expands/collapses, steps update during parse

- [ ] T026 [US1] Build extracted_data.html partial at `templates/partials/extracted_data.html`
  - Grid of key-value pairs (Price, Address, Units, Cap Rate, etc.)
  - "Calculator populated" indicator with gold dot
  - 📚 MCP: N/A (pure Jinja2 template, no library needed)
  - **DoD**: Extracted data renders as bullet points in system chat bubble

- [ ] T027 [US1] Wire GET / to render full page with query params at `backend/routes/pages.py`
  - Read all query params, parse into CalculatorInput (with defaults for missing)
  - Pre-render results if params present (shareable URL loads with results)
  - Serve templates/index.html with context
  - 📚 MCP: Context7 query "/websites/fastapi_tiangolo" for "request query_params optional parameters"
  - **DoD**: Opening `/?property_type=Commercial&purchase_price=1970000&...` shows pre-filled calculator with results

**Checkpoint**: MVP complete. Paste listing → parse → auto-populate → calculate → verdict → share via URL. All on one page, no full-page refresh.

---

## Phase 4: User Story 2 — Adjust Parameters with Instant Feedback (Priority: P1)

**Goal**: Slider/input changes update results instantly via HTMX partial swap
**Independent Test**: Move vacancy slider → only results panel updates, no page flicker

### Tests for User Story 2

- [ ] T028 [P] [US2] Integration test for partial swap behavior in `tests/integration/test_partial_swap.py`
  - Test: POST /calculate returns ONLY the results partial (not full page)
  - Test: response Content-Type is text/html
  - Test: response does NOT contain `<head>` or `<body>` tags (it's a fragment)
  - 📚 MCP: Context7 query "/websites/fastapi_tiangolo" for "TestClient response text content type"
  - **DoD**: Tests written and FAIL

### Implementation for User Story 2

- [ ] T029 [US2] Ensure hx-trigger="change" on all sidebar inputs (verify T019, T020)
  - Audit all form inputs have: `hx-post="/calculate"`, `hx-trigger="change"`, `hx-target="#results"`, `hx-include="[name]"`
  - Add `hx-trigger="input changed delay:300ms"` for sliders (debounce)
  - Add `hx-indicator="#calc-spinner"` for loading state
  - 📚 MCP: Context7 query "/bigskysoftware/htmx" for "hx-trigger input changed delay debounce hx-indicator"
  - **DoD**: `pytest tests/integration/test_partial_swap.py` PASSES, manual test confirms no page flicker on slider drag

- [ ] T030 [US2] Property type toggle swaps sidebar form
  - Clicking "Residential" / "Commercial" buttons swaps the sidebar partial via `hx-get="/sidebar/residential"` or `hx-get="/sidebar/commercial"`
  - Create GET endpoints that return sidebar partials
  - Results also recalculate with new type
  - 📚 MCP: Context7 query "/bigskysoftware/htmx" for "hx-get hx-target swap sidebar content"
  - **DoD**: Toggle works, sidebar swaps, results recalculate with correct formulas

**Checkpoint**: Calculator feels instant. No page refresh on any interaction.

---

## Phase 5: User Story 3 — Share Analysis via URL (Priority: P2)

**Goal**: Copy shareable link that reproduces exact analysis

### Tests for User Story 3

- [ ] T031 [P] [US3] Integration test for URL state preservation in `tests/integration/test_url_state.py`
  - Test: POST /calculate returns HX-Push-Url header with all form params
  - Test: GET / with full query params returns pre-rendered results
  - Test: round-trip — submit form → get URL → load URL → same results
  - 📚 MCP: Context7 query "/bigskysoftware/htmx" for "HX-Push-Url response header"
  - **DoD**: Tests written and FAIL

### Implementation for User Story 3

- [ ] T032 [US3] Add "Copy Share Link" button functionality
  - JavaScript: copy `window.location.href` to clipboard
  - Show toast notification "Link copied!"
  - Ensure HX-Push-Url is set correctly in /calculate response (from T022)
  - 📚 MCP: Context7 query "/bigskysoftware/htmx" for "hx-push-url true response headers"
  - **DoD**: `pytest tests/integration/test_url_state.py` PASSES, copy button works in browser

**Checkpoint**: Team can share exact analyses via URL.

---

## Phase 6: User Story 4 — Save to Portfolio (Priority: P2)

**Goal**: Save parsed + calculated data to Google Sheet

### Tests for User Story 4

- [ ] T033 [P] [US4] Integration test for save endpoint in `tests/integration/test_save.py`
  - Test: POST /api/properties with valid data returns {"status": "saved", "row": N}
  - Test: POST /api/properties with invalid data returns 400 error
  - Test: GET /api/properties returns list of saved deals with expected columns
  - 📚 MCP: Context7 query "/burnash/gspread" for "append_rows value_input_option USER_ENTERED"
  - **DoD**: Tests written and FAIL (or skip if no creds)

### Implementation for User Story 4

- [ ] T034 [US4] Create Sheets routes at `backend/routes/sheets.py`
  - POST /api/properties → calls sheets service append_property
  - GET /api/properties → calls sheets service get_all_properties
  - Mount in server.py
  - 📚 MCP: Context7 query "/websites/fastapi_tiangolo" for "APIRouter prefix tags"
  - **DoD**: `pytest tests/integration/test_save.py` PASSES

- [ ] T035 [US4] Add "Save to Portfolio" button in results partial
  - Button with `hx-post="/api/properties"` `hx-include="[name]"` — sends all current form values + calculated metrics
  - Show success/error toast response
  - Update "Last saved" timestamp in action bar
  - 📚 MCP: Context7 query "/bigskysoftware/htmx" for "hx-post response handling swap none"
  - **DoD**: Click Save → data appears in Google Sheet → toast shows "Saved to row N"

- [ ] T036 [US4] Build portfolio_table.html partial at `templates/partials/portfolio_table.html`
  - Sortable table: Address, Price, Cap Rate, CoC, DSCR, Verdict, Date
  - Each row clickable → loads deal into calculator via `hx-get="/?params"` `hx-push-url="true"`
  - Summary cards at top: total deals, avg cap rate, good/bad ratio
  - 📚 MCP: Context7 query "/bigskysoftware/htmx" for "hx-get click row table trigger"
  - **DoD**: Portfolio tab shows all saved deals from Sheet, clicking loads deal into Analyze tab

**Checkpoint**: Full pipeline works: Parse → Analyze → Save → Browse portfolio.

---

## Phase 7: User Story 5 — Compare Deals (Priority: P3)

**Goal**: Side-by-side comparison of 2-3 deals from portfolio

### Tests for User Story 5

- [ ] T037 [P] [US5] Integration test for compare endpoint in `tests/integration/test_compare.py`
  - Test: GET /compare?rows=2,5,10 returns HTML with 3 columns of metrics
  - Test: response highlights best value per metric
  - 📚 MCP: Context7 query "/bigskysoftware/htmx" for "hx-vals JSON values include parameters"
  - **DoD**: Tests written and FAIL

### Implementation for User Story 5

- [ ] T038 [US5] Create GET /compare route
  - Accept `rows` query param (comma-separated row numbers)
  - Fetch those rows from Sheets, calculate metrics for each
  - Return rendered `partials/compare_columns.html`
  - 📚 MCP: Context7 query "/burnash/gspread" for "get row by index specific rows"
  - **DoD**: `pytest tests/integration/test_compare.py` PASSES

- [ ] T039 [US5] Build compare_columns.html partial
  - Checkbox selection UI in portfolio table
  - "Compare Selected" button
  - Side-by-side columns with metrics, best value highlighted (bold, green)
  - 📚 MCP: Context7 query "/bigskysoftware/htmx" for "checkbox form include selected values"
  - **DoD**: Select 3 deals → click Compare → see side-by-side metrics with winner highlighted

**Checkpoint**: Compare works independently.

---

## Phase 8: User Story 6 — Mobile Layout (Priority: P3)

**Goal**: App works on phones (portrait + landscape)

### Tests for User Story 6

- [ ] T040 [P] [US6] E2E test for mobile viewports in `tests/e2e/test_mobile.py`
  - Test: 390px viewport shows tabbed nav (Parse / Analyze / Saved)
  - Test: all content scrollable (verdict, metrics, sliders, tables, buttons reachable)
  - Test: slider thumbs ≥20px touch target
  - Test: 844px landscape shows split view
  - 📚 MCP: Context7 query "/microsoft/playwright-python" for "set viewport size mobile emulation"
  - **DoD**: Tests written and FAIL

### Implementation for User Story 6

- [ ] T041 [US6] Add responsive CSS to theme.css
  - `@media (max-width: 768px)` — stack panels, show tab nav, hide chat panel in Analyze tab
  - `@media (min-width: 768px) and (max-width: 1023px)` — split view (42%/58%)
  - Slider thumb size ≥20px, touch targets ≥44px
  - Safe area padding for notched phones
  - 📚 MCP: Context7 query "/bigskysoftware/htmx" for "mobile responsive AJAX"
  - **DoD**: `pytest tests/e2e/test_mobile.py` PASSES, manual check on phone-sized browser

**Checkpoint**: Mobile works independently.

---

## Phase 8.5: Residential Results + OG Tags + Property Image

**Purpose**: Complete residential parity, rich link sharing, and property image integration

### Tests

- [ ] T047 [P] Unit test for residential calculator in `tests/unit/test_calculator_residential.py`
  - Test: 3 occupancy scenarios (75%/90%/100%) return correct cash flow and ROI
  - Test: amortization schedule first 12 months match Excel values
  - Test: investment status "Good" when profitable at 75%, "High Risk" when not
  - 📚 MCP: Context7 query "/python/cpython" for "decimal quantize financial amortization schedule"
  - **DoD**: Tests written and FAIL

- [ ] T048 [P] Integration test for OG meta tags in `tests/integration/test_og_tags.py`
  - Test: GET /?address=252+W+11th&price=1970000 → response contains `<meta property="og:title"` with address and price
  - Test: GET /?address=... → response contains `og:description` with metrics
  - Test: GET / with no params → generic OG tags (app name, default description)
  - 📚 MCP: Context7 query "/websites/fastapi_tiangolo" for "Jinja2Templates context request query params"
  - **DoD**: Tests written and FAIL

### Implementation

- [ ] T049 Build residential results in `templates/partials/results_residential.html`
  - Monthly expenses table: P&I, Insurance, Tax, PM (10%), Maintenance ($250)
  - 3 occupancy scenarios table: 75%/90%/100% with cash flow + ROI (green if positive, red if negative)
  - Investment status banner: ✅ Good Investment / ❌ High Risk (based on 75% occupancy)
  - Amortization schedule: first 12 months (Payment#, Principal, Interest, Balance)
  - Same verdict banner + metric cards as commercial
  - 📚 MCP: Context7 query "/bigskysoftware/htmx" for "hx-swap innerHTML partial template"
  - **DoD**: `pytest tests/unit/test_calculator_residential.py` PASSES, residential results render correctly

- [ ] T050 Add `Image_URL` field to parser schema
  - Add 16th field to `backend/schemas/property.py`: `Image_URL: str | None = None`
  - Update OpenAI extraction prompt to include image URL extraction
  - Update `Property-Prompt.md` with Image_URL field definition
  - 📚 MCP: Context7 query "/websites/fastapi_tiangolo" for "pydantic model optional field None"
  - **DoD**: Parser extracts image URL from test listings that have images, returns None for text-only

- [ ] T051 Add dynamic OG meta tags to `templates/base.html`
  - Read query params in GET / route, pass to template context
  - Render `<meta property="og:title" content="{{ address }} — {{ price }} · {{ units }} Units">`
  - Render `<meta property="og:description" content="Cap Rate: {{ cap_rate }} | CoC: {{ coc }} | {{ verdict }}">`
  - Render `<meta property="og:image" content="{{ image_url }}">`  if image_url present
  - Fallback: generic app title/description when no params
  - 📚 MCP: Context7 query "/websites/fastapi_tiangolo" for "Jinja2 template conditional meta tags"
  - **DoD**: `pytest tests/integration/test_og_tags.py` PASSES, SMS share preview shows property info

- [ ] T052 Add property image as blurred background
  - When `Image_URL` is in query params or parsed data, set as CSS `background-image` on results panel
  - Apply: `filter: blur(20px); opacity: 0.08;` overlay — subtle, doesn't interfere with readability
  - Fallback: default design (no image = no background image layer)
  - 📚 MCP: Context7 query "/bigskysoftware/htmx" for "CSS background image dynamic"
  - **DoD**: Property with image shows subtle background, property without image shows default design

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Cleanup, documentation, final quality

- [ ] T042 [P] Remove dead code and files
  - Delete: `scrape.js`, `node_modules/`, `package.json`, `package-lock.json`
  - Delete: `frontend/` directory (merged into templates/)
  - Move: `app.py` → `archive/app.py.bak` (keep for reference, remove from runtime)
  - Move: `*.xlsx` → `docs/reference/`
  - Move: `n8n-backups/` → `archive/n8n-backups/`
  - Update `.gitignore`: add `archive/`, `venv/`, `__pycache__/`
  - 📚 MCP: N/A
  - **DoD**: `git status` shows only tracked files, no orphans, `ruff check .` still passes

- [ ] T043 [P] Update README.md
  - New architecture description (FastAPI + HTMX, no Streamlit)
  - Updated setup instructions (quickstart.md content)
  - Screenshots of dark + light mode, desktop + mobile
  - API documentation
  - Google Sheets setup instructions
  - 📚 MCP: N/A
  - **DoD**: README accurately describes the current app, setup works from scratch following instructions

- [ ] T044 Update Azure deployment
  - Update `.github/workflows/azure-deploy.yml` startup command: `uvicorn server:app --host 0.0.0.0 --port 8000`
  - Remove Streamlit-specific config
  - Add `GOOGLE_SERVICE_ACCOUNT` and `GOOGLE_SHEET_ID` to Azure App Service settings
  - Test deployment
  - 📚 MCP: mslearn search "Azure App Service Python FastAPI deployment configuration"
  - **DoD**: Production URL responds, all functionality works on Azure

---

## Phase 10: E2E Validation (FINAL — Definition of Done)

**Purpose**: Playwright browser tests confirm EVERY section works. Project is NOT done until these pass.

- [ ] T045 Write comprehensive E2E test suite at `tests/e2e/test_full_flow.py`
  - Use Playwright MCP server / pytest-playwright
  - Test 1: App loads at root URL, header shows "405 Network"
  - Test 2: Chat panel accepts text input, "Parse Listing" button visible
  - Test 3: Paste listing text → pipeline steps appear → extracted data shows as bullets
  - Test 4: Calculator form auto-populates with parsed values
  - Test 5: Change vacancy slider → metric cards update WITHOUT page refresh (check no `<head>` in response)
  - Test 6: Verdict banner shows with correct color (green/amber/red) and 3 reasons
  - Test 7: All 7 metric cards render with non-zero values
  - Test 8: Property type toggle switches sidebar form
  - Test 9: Dark/light mode toggle works (check `data-theme` attribute)
  - Test 10: "Share Link" copies URL, opening URL in new tab shows same results
  - Test 11: "Save to Portfolio" writes to Google Sheet (verify via API read-back)
  - Test 12: Portfolio tab shows saved deals in table
  - Test 13: Compare tab shows side-by-side metrics for selected deals
  - Test 14: Mobile viewport (390px) shows tabbed layout, all content scrollable
  - 📚 MCP: Context7 query "/microsoft/playwright-python" for "page click fill expect locator assertions"
  - **DoD**: ALL 14 tests pass. This IS the project-level Definition of Done.

- [ ] T046 Run full validation suite and fix any failures
  - `ruff check .` → zero errors
  - `djlint templates/` → zero errors
  - `pytest tests/unit/ -v` → all green
  - `pytest tests/integration/ -v` → all green
  - `pytest tests/e2e/ -v` → all green (14/14 pass)
  - If ANY test fails → fix and re-run until green
  - 📚 MCP: N/A
  - **DoD**: Complete clean run of all lints + all tests + E2E. Zero failures. Project is DONE.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundation)**: Depends on Phase 1 — BLOCKS all user stories
- **Phase 3 (US1 MVP)**: Depends on Phase 2 (calculator, verdict, schemas, Jinja2)
- **Phase 4 (US2 Instant)**: Depends on Phase 3 (sidebar forms must exist)
- **Phase 5 (US3 Share)**: Depends on Phase 3 (calculate endpoint must exist)
- **Phase 6 (US4 Portfolio)**: Depends on Phase 2 (sheets service) + Phase 3 (results partial)
- **Phase 7 (US5 Compare)**: Depends on Phase 6 (portfolio must exist)
- **Phase 8 (US6 Mobile)**: Depends on Phase 3 (UI must exist to make responsive)
- **Phase 9 (Polish)**: Depends on Phase 3 (MVP must work before cleanup)
- **Phase 10 (E2E)**: Depends on ALL previous phases — final validation

### Parallel Opportunities

- T003 + T004 (linting + pytest config)
- T006 + T007 + T010 (states + thresholds + schemas — different files)
- T013 + T014 (US1 tests — different test files)
- T015 + T016 + T017 (CSS + JS + base template — different files)
- T019 + T020 (commercial + residential sidebars)
- Phase 5 + Phase 6 can run in parallel after Phase 3
- Phase 7 + Phase 8 can run in parallel after Phase 6

---

## Notes

- Total tasks: 52
- TDD tasks: 38 (every implementation task has tests first)
- MCP breadcrumbs: 52/52 tasks have a 📚 query
- Every task has a specific Definition of Done
- Phase 10 (E2E) is the project-level Definition of Done — 14+ Playwright tests must ALL pass
