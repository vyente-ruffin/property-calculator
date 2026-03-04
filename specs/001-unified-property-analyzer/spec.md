# Feature Specification: Property Analyzer — Unified Single-Page App

**Feature Branch**: `unified-property-analyzer`
**Created**: 2026-03-04
**Status**: Draft
**Input**: Consolidate separate Streamlit calculator + FastAPI parser + Google Sheets pipeline into a single-page investment screening tool for multifamily real estate investors.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Paste Listing & Get Investment Verdict (Priority: P1)

An investor finds a multifamily listing on LoopNet, TheMLS, or receives it via email. They paste the raw listing text (or a URL) into the chat panel. The system extracts structured property data via the 7-step AI pipeline, auto-populates the calculator, computes all investment metrics, and displays a color-coded verdict (INVEST / REVIEW / PASS) with supporting reasons. The entire flow happens on one page without navigation.

**Why this priority**: This is the core value proposition — the thing no competitor does. Paste → Verdict in under 60 seconds.

**Independent Test**: Paste sample listing text into the chat input, verify all 15 fields are extracted, metrics are calculated, and a verdict banner appears with at least 3 reasons.

**Acceptance Scenarios**:

1. **Given** the app is loaded, **When** a user pastes 8-unit listing text and clicks "Parse Listing", **Then** the chat shows collapsible pipeline progress (7 steps), extracted data as bullet points, and the calculator panel auto-fills with Purchase Price, Gross Rents, NOI, Units, and State.
2. **Given** parsed data has populated the calculator, **When** calculation completes, **Then** the verdict banner shows INVEST (green), REVIEW (amber), or PASS (red) with exactly 3 supporting reasons.
3. **Given** the parser encounters a URL-only input, **When** the user pastes just a listing URL, **Then** the system scrapes the page via Playwright, extracts fields, and proceeds identically to text input.
4. **Given** a listing is missing required fields (e.g., no NOI provided), **When** extraction completes, **Then** the chat shows which fields are missing and the calculator uses default values with a visual indicator.

---

### User Story 2 - Adjust Deal Parameters with Instant Feedback (Priority: P1)

After auto-population, the investor adjusts parameters using sliders (down payment %, vacancy rate, interest rate, loan term) and number inputs (purchase price, gross rents, NOI, expenses, units). Every change updates only the results area — no full-page refresh. Metric cards re-color based on new thresholds.

**Why this priority**: This is the daily workflow — investors tweak assumptions to stress-test deals. Must feel instant.

**Independent Test**: Move the vacancy slider from 3% to 15%. Verify only the results panel updates, metrics re-color, and the verdict may change from REVIEW to PASS.

**Acceptance Scenarios**:

1. **Given** calculator is showing results, **When** user drags the vacancy slider from 3% to 15%, **Then** only the results area updates (no page refresh), NOI decreases, DSCR drops, and metric card colors update accordingly.
2. **Given** calculator is showing results, **When** user changes purchase price from $1.97M to $1.5M, **Then** Cap Rate increases, Cash-on-Cash improves, and verdict may change from REVIEW to INVEST.
3. **Given** user has made custom adjustments, **When** user changes property type from Commercial to Residential, **Then** the sidebar inputs switch to residential fields (monthly rent, loan term 15/30 selectbox) and results recalculate with residential formulas.

---

### User Story 3 - Share Analysis via URL (Priority: P2)

The investor copies a shareable link that encodes all current calculator state (property type, all input values, property URL). A team member opens the link and sees the exact same analysis — same inputs, same metrics, same verdict.

**Why this priority**: Team collaboration depends on shareable analysis. This is a proven feature from the existing Streamlit app.

**Independent Test**: Click "Share Link", open the URL in an incognito window, verify all inputs match and metrics are identical.

**Acceptance Scenarios**:

1. **Given** calculator shows results for a commercial property, **When** user clicks "Share Link", **Then** the browser URL updates with all parameters and is copied to clipboard.
2. **Given** a shared URL with query parameters, **When** a new user opens it, **Then** the calculator loads with all inputs pre-filled, correct property type selected, and metrics displayed.
3. **Given** a shared URL, **When** the recipient adjusts a slider, **Then** the URL updates in real-time reflecting the new state.

---

### User Story 4 - Save to Portfolio (Priority: P2)

After analyzing a deal, the investor clicks "Save to Portfolio" to persist the parsed data + calculated metrics. The data is written to Google Sheets (and optionally to n8n webhook). The Portfolio tab shows all saved deals in a sortable table.

**Why this priority**: Without persistence, each analysis is ephemeral. The team needs a shared deal pipeline.

**Independent Test**: Analyze a deal, click Save, switch to Portfolio tab, verify the deal appears with correct metrics.

**Acceptance Scenarios**:

1. **Given** a fully analyzed deal, **When** user clicks "Save to Portfolio", **Then** 15 parsed fields + 6 calculated fields (Cap Rate, CoC, DSCR, Price/Unit, Verdict, Analyze URL) are written to Google Sheets.
2. **Given** saved deals exist, **When** user opens the Portfolio tab, **Then** deals display in a sortable table with columns: Address, Price, Cap Rate, CoC, DSCR, Verdict, Date.
3. **Given** a deal is in the Portfolio, **When** user clicks on it, **Then** the Analyze tab loads with that deal's data pre-filled.
4. **Given** Google Sheets is unreachable, **When** user clicks Save, **Then** the system shows an error toast and does NOT lose the data.

---

### User Story 5 - Compare Deals Side-by-Side (Priority: P3)

The investor selects 2-3 deals from the Portfolio and views them in a side-by-side comparison with metrics in columns. The best value for each metric is highlighted.

**Why this priority**: Comparison is the final step before making an investment decision. High value but depends on Portfolio being built first.

**Independent Test**: Save 3 deals, go to Compare, select all 3, verify metrics display in columns with winner highlighted per row.

**Acceptance Scenarios**:

1. **Given** 3 deals in Portfolio, **When** user selects them for comparison, **Then** a side-by-side view shows Cap Rate, CoC, DSCR, NOI, Price/Unit, Break-Even for each deal in columns.
2. **Given** comparison view is active, **When** user looks at each metric row, **Then** the best value is visually highlighted (bold, green accent).

---

### User Story 6 - Mobile On-Site Analysis (Priority: P3)

An investor visits a property and pulls up the app on their phone. They can paste listing details, see the verdict, adjust sliders with touch, and save the deal — all from a mobile browser.

**Why this priority**: On-site analysis is a real use case but secondary to desktop workflow.

**Independent Test**: Open the app on a 390px viewport, paste a listing, verify all content is scrollable, sliders are touch-friendly (≥20px thumb), and Save button is reachable.

**Acceptance Scenarios**:

1. **Given** mobile portrait view (<768px), **When** user loads the app, **Then** the layout shows tabbed navigation (Parse / Analyze / Saved) with full-width content.
2. **Given** mobile landscape view, **When** user rotates phone, **Then** the layout shows chat left + calculator right (split view).
3. **Given** mobile view, **When** user scrolls the Analyze tab, **Then** all content is reachable: verdict, metrics, sliders, expenses, analysis, summary, and action buttons.

---

### Edge Cases

- What happens when listing text contains no structured data (e.g., just a property description with no numbers)? → Parser extracts what it can, missing fields show as "--", calculator uses defaults.
- How does system handle listings with multiple properties in one paste? → Parser extracts the first/primary property only, chat warns about additional properties detected.
- What if Rentcast API is down or returns no data? → Pipeline step shows "skipped" status, projected rent fields remain null, calculator uses only provided data.
- What if user pastes a listing URL from a site that blocks scrapers (LoopNet, Crexi)? → Scrape step fails gracefully, chat shows error with suggestion to paste text instead.
- What if the Google Sheets service account auth expires? → Save fails with actionable error message, analysis is not lost, user can still share via URL.
- What if two team members save the same property? → Duplicate row is created (by design — Sheets handles it). Future: dedup by address.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST serve both the UI and API from a single FastAPI process on a single port.
- **FR-002**: System MUST render the chat panel and calculator panel side-by-side on desktop (≥1024px).
- **FR-003**: System MUST render tabbed navigation (Parse / Analyze / Saved) on mobile (<768px).
- **FR-004**: System MUST accept raw listing text or URLs in the chat input and stream 7-step pipeline progress via SSE.
- **FR-005**: System MUST auto-populate calculator inputs from parsed property data (Price → Purchase Price, Annual Rent Income → Gross Rents, NOI → Annual NOI, City → State extraction, Total Units → Units, Link → Property URL).
- **FR-006**: System MUST calculate and display: Cap Rate, Cash-on-Cash Return, DSCR, NOI (estimated), Price/Unit, Break-Even Occupancy, GRM.
- **FR-007**: System MUST show a verdict banner (INVEST/REVIEW/PASS) with 3 supporting reasons based on metric thresholds.
- **FR-008**: System MUST show Broker NOI vs Estimated NOI comparison with delta percentage and alert if gap >15%.
- **FR-009**: System MUST update only the results area on input changes (HTMX partial swap), NOT the full page.
- **FR-010**: System MUST support both Residential (≤4 units) and Commercial (5+ units) property types with different calculation formulas.
- **FR-011**: System MUST persist shareable state in URL query parameters, updated on every input change via `hx-push-url`.
- **FR-012**: System MUST read from and write to Google Sheets via gspread with a service account (no n8n, no user login). Service account credentials stored as env variable. Sheet shared with service account email.
- **FR-013**: System MUST provide adjustable sliders for: Down Payment %, Vacancy Rate %, Interest Rate %, and Loan Term.
- **FR-014**: System MUST display operating expenses table (P&I, Insurance, Taxes, PM Fee, Other) with monthly and annual columns.
- **FR-015**: System MUST display investment analysis table (Gross Rents, Adjusted Gross, NOI, Debt Service, Cash Flow, CoC, Cash Down).
- **FR-016**: System MUST display investment summary grid (Purchase Price, Loan Amount, Down Payment, Monthly Payment, Closing Costs, NOI, Total Cash, Cash Flow).
- **FR-017**: System MUST provide color-coded metric cards with threshold-based coloring (green/amber/red) and 2px top accent bars.
- **FR-018**: System MUST support state-specific tax and insurance rates for AZ, CA, IN, NV, TX, MI.
- **FR-019**: System MUST support light and dark color themes toggled via a switch in the header. Dark mode is default. Both themes MUST use CSS variables. Signal colors MUST remain legible in both.
- **FR-020**: System MUST pin all Python dependencies to exact versions in requirements.txt.
- **FR-021**: System MUST pass `ruff check .` and `djlint templates/` with zero errors before deployment.
- **FR-022**: Residential results MUST show: Monthly Expenses Table (P&I, Insurance, Tax, PM 10%, Maintenance $250), 3 Occupancy Scenarios (75%/90%/100% with cash flow and ROI, color-coded), Investment Status Banner (profitable at 75% = ✅, not = ❌), Amortization Schedule (first 12 months), and the same verdict + metric cards as commercial.
- **FR-023**: System MUST render dynamic Open Graph meta tags per property URL so SMS/social link previews show: property address + price + units as title, key metrics as description, and property image as og:image (if available).
- **FR-024**: Parser MUST extract a 16th field `Image_URL` (the listing's hero/primary image URL) when available from the source listing.
- **FR-025**: When `Image_URL` is available, the calculator panel MUST use the property image as a subtle, blurred background behind the results area. If unavailable, fall back to the default design.

## Clarifications

### Session 2026-03-04

- Q: Where should saved deals be stored? → A: Google Sheets directly via gspread (eliminate n8n entirely). App handles read/write. Save button writes to Sheet, Portfolio tab reads from Sheet.
- Q: How should the app read portfolio data back from Google Sheets? → A: Direct gspread read from the app's FastAPI backend. No n8n intermediary.
- Q: What Google Sheets auth method? → A: Service Account (server-side JSON key stored as env variable). Share Sheet with service account email. No user login required.
- Q: How to handle the existing 21-column Google Sheet schema? → A: Keep existing columns intact, append new calculated columns (CoC, DSCR, Price/Unit, Break-Even, Verdict, Analyze URL) at the end after column U. Existing data and team's manual notes preserved.
- Q: What color direction for light mode? → A: Warm parchment/cream base (#f8f6f1) — luxury financial document feel. Gold accent stays warm.

### Key Entities

- **Property**: 15-field parsed data (Price, Address, City, Cap Rate, Date On Market, Monthly/Annual Rental Income Projected/Actual, NOI, Lot/Building Size, Total Units, Unit Mix Summary, Link, Description).
- **CalculationResult**: All computed metrics (Cap Rate, CoC, DSCR, NOI Estimated, Price/Unit, Break-Even Occ, GRM, Annual Cash Flow, Monthly Payment, Total Cash Down) plus verdict (INVEST/REVIEW/PASS with reasons).
- **PortfolioEntry**: Property + CalculationResult + metadata (saved_at, analyze_url).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can go from pasting raw listing text to seeing a color-coded investment verdict in under 60 seconds.
- **SC-002**: Input changes (slider drags, field edits) update results in under 100ms perceived latency — no visible page flicker.
- **SC-003**: All 7 investment metrics (Cap Rate, CoC, DSCR, NOI, Price/Unit, Break-Even, GRM) display correctly and match Excel-validated calculations within ±$1 rounding.
- **SC-004**: Shared URLs reproduce the exact same analysis (same inputs, same metrics, same verdict) when opened by a different user.
- **SC-005**: The app is fully usable on mobile devices (390px width) with all content scrollable and all interactive elements touch-accessible (≥44px touch targets).
- **SC-006**: Portfolio saves complete in under 3 seconds and appear in the Portfolio tab on next load.
