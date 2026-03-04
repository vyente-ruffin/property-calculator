# Security & Reliability Checklist: Unified Property Analyzer

**Purpose**: Validate credential handling, error resilience, and data integrity
**Created**: 2026-03-04
**Feature**: [spec.md](../spec.md)

## Credential Management

- [ ] CHK122 GOOGLE_SERVICE_ACCOUNT JSON never committed to git (verify .gitignore includes `.env`)
- [ ] CHK123 .env.example contains placeholder `GOOGLE_SERVICE_ACCOUNT={}` (not real credentials)
- [ ] CHK124 Service account JSON loaded from env var, NOT from a file on disk
- [ ] CHK125 AZURE_OPENAI_API_KEY, RENTCAST_API_KEY not in any committed file
- [ ] CHK126 No API keys, tokens, or secrets appear in HTML source, JS files, or template output
- [ ] CHK127 Azure App Service env vars set via portal/CLI, not in deployment scripts

## Error Resilience

- [ ] CHK128 App starts and serves UI even if GOOGLE_SERVICE_ACCOUNT is missing (calculator works, Sheets features disabled)
- [ ] CHK129 App starts even if AZURE_OPENAI_API_KEY is missing (parser disabled, calculator works)
- [ ] CHK130 Google Sheets API timeout (>5s) returns error response, doesn't hang the request
- [ ] CHK131 Google Sheets API failure doesn't lose the user's current analysis (still on screen)
- [ ] CHK132 Rentcast API failure during parsing → step shows "skipped", parsing continues
- [ ] CHK133 Invalid listing text (gibberish) → parser returns partial data, doesn't crash
- [ ] CHK134 Extremely long listing text (>50KB) → handled without memory issues
- [ ] CHK135 Concurrent users (2-5) don't interfere with each other's calculations (stateless)

## Input Validation

- [ ] CHK136 Purchase price: rejects negative numbers, zero, and non-numeric input
- [ ] CHK137 Down payment: constrained to 0-100% range
- [ ] CHK138 Vacancy rate: constrained to 0-50% range
- [ ] CHK139 Interest rate: constrained to 0-20% range
- [ ] CHK140 Loan term: constrained to 1-30 years
- [ ] CHK141 Total units: constrained to ≥1, integer only
- [ ] CHK142 Division by zero prevented: 0 units, 0 gross rents, 0 purchase price → handled gracefully

## Data Integrity

- [ ] CHK143 Google Sheet existing data (235 rows, columns A-U) is NEVER modified by the app
- [ ] CHK144 New rows appended AFTER existing data (not inserted in the middle)
- [ ] CHK145 Column order in append matches exact Sheet header order (A through AA)
- [ ] CHK146 Currency values written with $ formatting (USER_ENTERED mode)
- [ ] CHK147 Percentage values written with % suffix
- [ ] CHK148 No duplicate rows created from double-clicking Save (debounce or disable during save)

## Deployment

- [ ] CHK149 Azure App Service B1 tier supports the app (no WebSocket requirement — SSE is plain HTTP)
- [ ] CHK150 Health check endpoint GET /api/health returns 200
- [ ] CHK151 Startup time <30s on Azure cold start
- [ ] CHK152 CDN dependencies (HTMX, DaisyUI, Tailwind, Fonts) load from versioned URLs (not "latest")
- [ ] CHK153 App works if CDN is slow (fonts fall back gracefully, HTMX/DaisyUI are required)

## Notes

- No user authentication — the app is open to anyone with the URL (by design, per clarification)
- Service account has Editor access to ONE specific Google Sheet — limited blast radius
- All calculations are stateless and server-side — no sensitive data in browser localStorage (only theme preference)
