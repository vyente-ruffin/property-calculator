# Financial Accuracy Checklist: Unified Property Analyzer

**Purpose**: Validate that all investment calculations match Excel references and industry standards
**Created**: 2026-03-04
**Feature**: [spec.md](../spec.md) — Principle III: Financial Accuracy First

## Calculation Formulas

- [ ] CHK001 Monthly P&I formula matches standard amortization: `P × [r(1+r)^n] / [(1+r)^n - 1]` where r=monthly_rate, n=total_payments
- [ ] CHK002 Commercial NOI Estimated: `(Gross × (1 - Vacancy%)) - (Insurance + Tax + PM + Other)` matches Excel cell `=(K4*(1-L5))-SUM(J8:J11)`
- [ ] CHK003 Residential monthly expense: PI + Insurance + Tax + PM(10%) + Maintenance($250) — all components verified
- [ ] CHK004 Cap Rate formula: `NOI ÷ Purchase Price × 100` — verified with at least 3 different property prices
- [ ] CHK005 DSCR formula: `NOI ÷ Annual Debt Service` — verified at boundary values (1.0, 1.25, 0.5)
- [ ] CHK006 Cash-on-Cash formula: `Annual Cash Flow ÷ Total Cash Invested × 100` where Total Cash = Down + Closing(3%)
- [ ] CHK007 Price/Unit formula: `Purchase Price ÷ Total Units` — verified with 1, 4, 8, 50 units
- [ ] CHK008 Break-Even Occupancy: `(OpEx + Debt Service) ÷ Gross Potential Rent × 100` — verified at 0% and 100% occupancy
- [ ] CHK009 GRM formula: `Purchase Price ÷ Annual Gross Rents` — verified non-zero denominator handling
- [ ] CHK010 Closing costs: exactly 3% of purchase price (commercial standard)
- [ ] CHK011 PM fee: 4% of gross rents (commercial) vs 10% of rent (residential)

## Precision & Rounding

- [ ] CHK012 All monetary calculations use Python `Decimal` — no float arithmetic anywhere in calculator.py
- [ ] CHK013 Monthly payment rounded to 2 decimal places (cents)
- [ ] CHK014 Annual totals rounded to whole dollars for display
- [ ] CHK015 Percentages display with 1 decimal place (e.g., "6.2%", not "6.19843%")
- [ ] CHK016 DSCR displays with 2 decimal places (e.g., "1.18×")
- [ ] CHK017 No rounding errors accumulate across chained calculations (test with Excel comparison)

## Excel Validation

- [ ] CHK018 Commercial test case (from spec): Purchase=$1,970,000, Down=30%, Rate=6.5%, Term=25yr, Gross=$152,195, NOI=$106,548, Vacancy=3%, Expenses=$5,000, State=CA → NOI_est matches Excel within ±$1
- [ ] CHK019 Same test case: Cash Flow, CoC, DSCR, Cap Rate all match Excel within rounding tolerance
- [ ] CHK020 Residential test case: Purchase=$650,000, Down=20%, Rate=6.5%, Term=15yr, Rent=$5,000, State=CA → monthly expenses match Excel
- [ ] CHK021 Residential 75%/90%/100% occupancy scenarios match Excel outputs

## State Data

- [ ] CHK022 All 6 state tax rates verified: AZ=0.62%, CA=1.25%, IN=1.37%, NV=0.65%, TX=1.70%, MI=3.21%
- [ ] CHK023 All 6 state insurance rates verified: AZ=0.50%, CA=1.25%, IN=0.50%, NV=0.50%, TX=0.50%, MI=0.50%
- [ ] CHK024 Changing state recalculates tax and insurance correctly (not cached from previous state)

## Metric Thresholds

- [ ] CHK025 Cap Rate: ≥6% → green, 4-6% → yellow, <4% → red — all 3 verified
- [ ] CHK026 CoC: ≥8% → green, 4-8% → yellow, <4% → red — all 3 verified
- [ ] CHK027 DSCR: ≥1.25 → green, 1.0-1.25 → yellow, <1.0 → red — all 3 verified
- [ ] CHK028 Break-Even: <75% → green, 75-85% → yellow, >85% → red — all 3 verified
- [ ] CHK029 Boundary values test: exact threshold values (e.g., 6.0% cap rate) go to the correct bucket

## Verdict Engine

- [ ] CHK030 INVEST verdict: triggered when ALL 4 scored metrics are green
- [ ] CHK031 PASS verdict: triggered when ANY metric is red, OR DSCR < 1.0
- [ ] CHK032 REVIEW verdict: triggered for all other combinations (mixed green/yellow)
- [ ] CHK033 Exactly 3 reasons returned for every verdict — no more, no less
- [ ] CHK034 Reasons reference specific metric values (e.g., "DSCR 1.18x below 1.25x threshold")

## Notes

- Financial accuracy is the #1 credibility factor for an investment tool
- Any calculation discrepancy vs Excel is a blocking bug
- Decimal precision is non-negotiable per constitution Principle III
