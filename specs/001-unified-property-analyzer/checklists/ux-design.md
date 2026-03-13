# UX & Design Checklist: Unified Property Analyzer

**Purpose**: Validate the UI matches mockups, is responsive, accessible, and follows the design system
**Created**: 2026-03-04
**Feature**: [spec.md](../spec.md) — Principle IV: Design System Consistency

## Design System Compliance

- [ ] CHK035 Typography: Bricolage Grotesque loads and renders for headings/brand
- [ ] CHK036 Typography: JetBrains Mono loads and renders for all financial numbers
- [ ] CHK037 Typography: Outfit loads and renders for body text and UI labels
- [ ] CHK038 Dark theme: midnight (#06090f) base, surface (#111827), gold (#d4a853) accent — all match mockup
- [ ] CHK039 Light theme: parchment (#f8f6f1) base, white surface, dark gold accent — all legible
- [ ] CHK040 Signal colors legible in BOTH themes: green (#34d399 dark / #16a34a light), amber, red
- [ ] CHK041 Theme toggle: click switches instantly, no flash of wrong theme on reload
- [ ] CHK042 Theme toggle: preference persists in localStorage across sessions
- [ ] CHK043 Metric cards: 2px top color bar matches signal color (green/amber/red)
- [ ] CHK044 Verdict banner: glow effect visible behind icon, correct color per verdict
- [ ] CHK045 Noise texture overlay visible in dark mode, absent or subtle in light mode

## Layout — Desktop (≥1024px)

- [ ] CHK046 Chat panel: 400px fixed width, left side
- [ ] CHK047 Calculator panel: fills remaining width, right side
- [ ] CHK048 Both panels scroll independently (not locked together)
- [ ] CHK049 Header spans full width with brand left, status dot right
- [ ] CHK050 Action bar (Save/Share/Compare) pinned to bottom of calculator panel

## Layout — Mobile Portrait (<768px)

- [ ] CHK051 Tabbed navigation visible: Parse / Analyze / Saved
- [ ] CHK052 Tabs switch content (not visible simultaneously)
- [ ] CHK053 ALL calculator content scrollable: verdict → metrics → sliders → expenses → analysis → summary → actions
- [ ] CHK054 No content cut off or hidden behind action bar
- [ ] CHK055 Metric cards: 2×2 grid (not 4-across)
- [ ] CHK056 Sliders: thumb ≥20px, touch target ≥44px

## Layout — Mobile Landscape (768-1023px)

- [ ] CHK057 Split view: chat left (42%), calculator right (58%)
- [ ] CHK058 Metric cards: 4-across (fit in wider view)
- [ ] CHK059 Both panels scroll independently

## Interaction

- [ ] CHK060 Slider drag updates displayed value in real-time (JS, no server round-trip)
- [ ] CHK061 Slider release triggers HTMX calculation (debounced 300ms)
- [ ] CHK062 Number input change triggers recalculation on blur/change
- [ ] CHK063 State dropdown change triggers recalculation immediately
- [ ] CHK064 No visible flicker/flash when results update (partial swap, not full page)
- [ ] CHK065 Loading indicator shows during calculation (if >100ms)
- [ ] CHK066 Pipeline steps animate sequentially during parsing (not all at once)
- [ ] CHK067 Pipeline steps container is collapsible (click to expand/collapse)
- [ ] CHK068 Extracted data appears as bullet points in chat after parsing

## Content Completeness (vs. existing Streamlit app)

- [ ] CHK069 Commercial: Operating expenses table shows P&I, Insurance, Tax, PM, Other — monthly AND annual
- [ ] CHK070 Commercial: Investment analysis table shows Gross, Adj Gross, NOI, Debt Service, Cash Flow, CoC, Cash Down
- [ ] CHK071 Commercial: Investment summary grid shows Purchase, Loan, Down, Monthly, Closing, NOI, Total Cash, Cash Flow
- [ ] CHK072 Commercial: Amount down badge shows color (green ≤$500K, yellow $500-750K, red >$750K)
- [ ] CHK073 Residential: Monthly expenses table shows P&I, Insurance, Tax, PM, Maintenance
- [ ] CHK074 Residential: 75%/90%/100% occupancy scenarios with color-coded cash flow
- [ ] CHK075 Residential: Investment status banner (profitable at 75% = ✅, not = ❌)
- [ ] CHK076 "View Property Listing" link opens in new tab when URL is present
- [ ] CHK077 NOI comparison shows broker vs estimated with delta % and warning if >15% gap

## Notes

- Reference mockups: `mockup.html` (desktop), `mockup-mobile.html` (portrait + landscape)
- Every UX item is visually verifiable — no abstract metrics
- Mobile testing requires actual device or browser DevTools device emulation
