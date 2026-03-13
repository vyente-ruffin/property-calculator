# Property Analyzer Constitution
<!-- Sync Impact Report
Version: 1.1.0 → 2.0.0 (MAJOR: added TDD mandate, version pinning, linting, Definition of Done, E2E validation, light/dark mode, MCP breadcrumbs)
Added: Principle VI (TDD), Version Pinning & Linting section, Definition of Done section, E2E Validation section, Light/Dark Mode to Design System
Modified: Testing section (expanded to TDD mandate), Design System (added theme toggle)
Removed: None
Templates requiring updates: ✅ spec-template.md | ✅ plan-template.md | ✅ tasks-template.md
Follow-up TODOs: None
-->

# Property Analyzer Constitution

## Core Principles

### I. Single-Page Investment Tool
The application MUST present parsing, analysis, and portfolio management as a unified single-page experience. The chat-based listing parser and the investment calculator MUST coexist on one screen (side-by-side on desktop, tabbed on mobile). Users MUST never navigate away from the page to complete the workflow: paste listing → parse → analyze → save.

### II. No Full-Page Refresh
Every user interaction (slider drag, input change, tab switch) MUST update only the affected UI region. Full-page reloads and framework-induced re-renders are prohibited. The frontend MUST use HTMX partial swaps or equivalent for server-rendered updates, and client-side JS for immediate input feedback. Streamlit is explicitly excluded as a frontend framework. **Exception**: Initial page loads from a shared URL or direct navigation are exempt — "no refresh" applies only to interactions WITHIN an already-loaded page.

### III. Financial Accuracy First
All monetary calculations MUST use precise arithmetic (Python `Decimal` or equivalent). Formulas MUST match the validated Excel references (`Commercial_Prop_Screening_Tool.xlsx`, `Residential_Prop_Screening_Tool.xlsx`). Every metric (Cap Rate, DSCR, CoC, NOI, GRM, Break-Even Occupancy, Price/Unit) MUST display with appropriate precision and color-coded thresholds. The verdict engine (INVEST/REVIEW/PASS) MUST score across at least 4 independent metrics.

### IV. Design System Consistency
The UI MUST follow the "Private Equity Command Deck" design system established in the mockups. Typography: Bricolage Grotesque (headings), JetBrains Mono (financial numbers), Outfit (body). Color palette: midnight navy base with gold accent (#d4a853) for primary actions, signal colors for metrics (green/amber/red). All components MUST be responsive — desktop (side-by-side panels), mobile portrait (tabbed), and mobile landscape (split view). The app MUST support both **dark mode** (default — midnight navy) and **light mode** (warm off-white base) toggled via a UI switch. Both themes MUST use CSS variables so all colors swap cleanly. Signal colors (green/amber/red) MUST remain legible in both themes.

### V. Parser Pipeline Integrity
The existing 7-step async parser pipeline (parse_input → scrape_url → extract_fields → search_link → rentcast → reextract → validate) MUST be preserved. Pipeline progress MUST stream to the UI via Server-Sent Events. Parsed data MUST auto-populate calculator inputs. The 15-field property schema MUST remain the canonical data contract between parser and calculator.

### VI. Test-Driven Development (NON-NEGOTIABLE)
Every task MUST follow TDD: write failing tests FIRST, then implement code to make them pass, then refactor. No production code is written without a corresponding test that was red before green. This applies to:
- Calculator service functions (unit tests against Excel-validated outputs)
- Verdict engine (boundary condition tests for INVEST/REVIEW/PASS)
- API endpoints (integration tests for request/response contracts)
- Parser pipeline (integration tests for text-only, URL-only, text+URL)
- HTMX partials (rendered HTML fragment assertions)
- E2E flows (Playwright tests for full user journeys)

**Exception**: Non-code tasks (directory creation, file cleanup, README updates, deployment config) follow a **verification step** instead of Red-Green-Refactor. These tasks MUST define a concrete "verify" command (e.g., `ls -d templates/partials`, `ruff check .`, `curl -s https://app-url/ | grep "405 Network"`) that confirms the task is done. The verification step serves the same purpose as a test — proving the work is correct.

## Design System

### Visual Identity
- **Brand**: 405 Network — gold mark (4N) on midnight background
- **Fonts**: Bricolage Grotesque (display/headings), JetBrains Mono (numbers/data), Outfit (body/UI)
- **Dark Theme (default)**: Midnight (#06090f) base, surface (#111827), gold (#d4a853) accent, signal green (#34d399), caution amber (#fbbf24), alert red (#f87171)
- **Light Theme**: Off-white (#f8f6f1) base, surface (#ffffff), gold-dark (#a67c3b) accent, signal green (#16a34a), caution amber (#d97706), alert red (#dc2626)
- **Theme Toggle**: MUST use CSS variables (`--bg`, `--surface`, `--gold`, `--up`, `--caution`, `--down`, etc.) with `data-theme="dark|light"` attribute on `<html>`. Toggle switch in header.
- **Texture**: Subtle noise grain overlay, faint grid pattern for depth (dark mode only)
- **Components**: Metric cards with 2px top color bar, verdict banners with glow effect, pipeline step indicators

### Responsive Breakpoints
- **Desktop (≥1024px)**: Chat panel (400px fixed) + calculator panel (flex). Side-by-side layout.
- **Mobile Portrait (<768px)**: Tabbed navigation (Parse / Analyze / Saved). Full-width stacked content.
- **Mobile Landscape (768-1023px)**: Split view — chat left (42%), calculator right (58%). Compact metrics (4-across).

### Reference Mockups
- `mockup.html` — Desktop layout reference (dark mode)
- `mockup-mobile.html` — Portrait and landscape phone frames (dark mode)

## Development Workflow

### Tech Stack
- **Backend**: FastAPI (Python 3.11+) — serves both API and UI
- **Frontend**: HTMX + Jinja2 templates + Tailwind/DaisyUI — no React, no Streamlit
- **Parser**: Azure OpenAI (gpt-4o) + Rentcast API + Playwright scraping
- **Data Layer**: Google Sheets via gspread with service account (direct read/write from FastAPI). n8n eliminated.
- **Deployment**: Azure App Service (B1 tier), GitHub Actions CI/CD with OIDC auth
- **Testing**: pytest + pytest-asyncio (backend), Playwright (E2E)
- **Linting**: ruff (Python linting + formatting), djlint (Jinja2 template linting)

### Version Pinning & Linting
- ALL Python dependencies MUST be pinned to exact versions in `requirements.txt` (e.g., `fastapi==0.115.6`, NOT `fastapi>=0.115.0`). Use `pip freeze` after confirming working versions.
- ALL CDN dependencies (HTMX, DaisyUI, Tailwind, Google Fonts) MUST use versioned URLs, not `latest` or unversioned.
- **ruff** MUST be used for Python linting and formatting. Configuration in `pyproject.toml` with rules: `select = ["E", "F", "W", "I", "N", "UP", "B", "A", "C4", "SIM"]`.
- **djlint** MUST be used for Jinja2/HTML template linting.
- CI pipeline MUST run `ruff check .` and `djlint templates/` before tests. Lint failures block merge.

### Code Standards
- Backend calculation logic MUST live in `backend/services/` as pure functions (no UI coupling)
- Templates MUST live in `templates/` with partials in `templates/partials/` for HTMX swaps
- State data (tax rates, insurance rates, metric thresholds) MUST be in `backend/data/`
- All shareable URLs MUST use query parameters — `hx-push-url` for HTMX, standard `request.query_params` on load

### Testing (TDD Mandate)
- **Red-Green-Refactor cycle** is mandatory for every task:
  1. Write tests that define the expected behavior → tests MUST fail (Red)
  2. Write minimal code to make tests pass (Green)
  3. Refactor for clarity while keeping tests green (Refactor)
- Calculator service functions MUST have unit tests validating against Excel formula outputs
- Verdict engine MUST have tests for all three outcomes (INVEST/REVIEW/PASS) with boundary conditions
- Parser pipeline integration tests MUST exist for text-only, URL-only, and text+URL inputs
- HTMX endpoint tests MUST assert correct HTML fragment structure in response body
- E2E tests MUST use Playwright MCP server to navigate the running app and validate all sections

## Documentation & Knowledge Sources

### Single Points of Truth
- **Context7 MCP server** MUST be used for ALL code and documentation lookups for third-party libraries, frameworks, and APIs. This ensures answers are grounded in the latest official documentation, not stale training data.
- **Microsoft Learn MCP server** (`mslearn`) MUST be used for ALL Azure-related documentation, deployment configuration, and SDK usage. Use `microsoft_docs_search` for discovery and `microsoft_docs_fetch` for full content.
- **Web search and web fetch** MUST NOT be used for documentation lookups unless the user explicitly approves. Context7 and mslearn are authoritative — web search is a fallback of last resort.
- When implementing with any library (FastAPI, HTMX, Jinja2, gspread, Pydantic, etc.), the developer MUST query Context7 first to confirm API signatures, configuration patterns, and best practices before writing code.

### MCP Breadcrumbs in Tasks
- Every task in `tasks.md` MUST include an **MCP Breadcrumb** — a specific Context7 or mslearn query that the implementing agent should run to ground its work in authoritative documentation before writing code.
- Format: `📚 MCP: Context7 query "<library>" for "<specific topic>"` or `📚 MCP: mslearn search "<azure topic>"`
- This ensures the task-creating agent and the task-executing agent converge on the same answer via the same source of truth.

## Definition of Done

### Per-Task Definition of Done
Every individual task is NOT considered done until ALL of the following are true:
1. **Tests written first** — failing tests exist that define expected behavior
2. **Tests passing** — all tests for this task pass (Red → Green achieved)
3. **Lint clean** — `ruff check` and `djlint` report zero errors for changed files
4. **No regressions** — all pre-existing tests still pass
5. **Verified working** — the feature is manually or automatically confirmed functional (not just "code written")

### Project-Level Definition of Done
The unified Property Analyzer is NOT considered complete until ALL of the following are true:
1. **All tasks in tasks.md marked [X]** — every task completed per the per-task DoD above
2. **Full test suite passes** — `pytest` green, zero failures
3. **Lint suite passes** — `ruff check .` and `djlint templates/` zero errors
4. **E2E validation via Playwright** — automated browser tests confirm:
   - App loads at root URL
   - Chat panel accepts text input and displays pipeline progress
   - Parsed data auto-populates calculator fields
   - Slider changes update metrics without page refresh
   - Verdict banner displays with correct color and reasons
   - All 7 metrics render with correct values
   - Property type toggle switches forms correctly
   - Light/dark mode toggle works
   - Share link produces correct URL with all parameters
   - Save to Portfolio writes successfully
   - Portfolio tab displays saved deals
   - Compare tab shows side-by-side metrics
   - Mobile layout works at 390px and 844px viewports
5. **Deployed to Azure** — production URL responds and all E2E tests pass against it
6. **README updated** — reflects new architecture, setup instructions, and screenshots

## Governance

- This constitution supersedes all other development practices for the Property Analyzer project
- Amendments require documentation of what changed, why, and impact on existing code
- All PRs MUST verify compliance with Principles I-VI before merge
- The mockup files (`mockup.html`, `mockup-mobile.html`) are the visual source of truth until production CSS replaces them

**Version**: 2.0.0 | **Ratified**: 2026-03-04 | **Last Amended**: 2026-03-04
