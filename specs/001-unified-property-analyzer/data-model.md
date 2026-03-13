# Data Model: Property Analyzer

## Entities

### PropertyData (15-field canonical schema — existing)
Source: `backend/schemas/property.py`

| Field | Type | Format | Required |
|-------|------|--------|----------|
| Price | str \| None | "$X,XXX,XXX" | Yes |
| Address | str \| None | Street only | Yes |
| City | str \| None | "City, ST ZIP" | Yes |
| Cap_Rate | str \| None | "X.XX%" | No |
| Date_On_Market | str \| None | "YYYY-MM-DD" | No |
| Monthly_Rental_Income_Projected | str \| None | "$X,XXX" | Yes |
| Monthly_Rental_Income_Actual | str \| None | "$X,XXX" | No |
| Annual_Rent_Income_Projected | str \| None | "$X,XXX,XXX" | Yes |
| Annual_Rent_Income_Actual | str \| None | "$X,XXX,XXX" | No |
| NOI | str \| None | "$X,XXX,XXX" | No |
| Lot_building_size | str \| None | "X SF / Y SF" | No |
| Total_Units | int \| None | integer | Yes |
| Unit_Mix_Summary | str \| None | "QTY×BD/BA@$RENT" | No |
| Link | str \| None | URL | No |
| Description | str \| None | ≤200 chars | No |

### CalculatorInput (form values)

| Field | Type | Default | Range |
|-------|------|---------|-------|
| property_type | str | "Commercial" | "Residential" \| "Commercial" |
| purchase_price | Decimal | 1,970,000 | > 0 |
| down_payment_pct | Decimal | 30 | 0-100 |
| interest_rate | Decimal | 6.5 | 0-20 |
| loan_years | int | 25 | 1-30 |
| total_units | int | 8 | ≥ 1 |
| state | str | "CA" | AZ, CA, IN, NV, TX, MI |
| property_url | str | "" | URL or empty |
| **Commercial-specific** | | | |
| annual_gross_rents | Decimal | 152,195 | > 0 |
| annual_noi_listing | Decimal | 106,548 | ≥ 0 |
| vacancy_rate | Decimal | 3 | 0-50 |
| other_expenses | Decimal | 5,000 | ≥ 0 |
| **Residential-specific** | | | |
| monthly_rent | Decimal | 5,000 | > 0 |

### CalculationResult

| Field | Type | Formula |
|-------|------|---------|
| noi_estimated | Decimal | (Gross × (1 - Vacancy%)) - OpEx |
| noi_listing | Decimal | Input (broker's NOI) |
| noi_delta_pct | Decimal | (listing - estimated) / listing × 100 |
| cap_rate | Decimal | NOI ÷ Purchase Price × 100 |
| cash_on_cash | Decimal | Cash Flow ÷ Total Cash × 100 |
| dscr | Decimal | NOI ÷ Annual Debt Service |
| price_per_unit | Decimal | Purchase Price ÷ Total Units |
| breakeven_occ | Decimal | (OpEx + Debt Service) ÷ Gross × 100 |
| grm | Decimal | Purchase Price ÷ Annual Gross Rents |
| annual_cash_flow | Decimal | NOI - Annual Debt Service |
| monthly_payment | Decimal | Standard amortization formula |
| annual_debt_service | Decimal | monthly_payment × 12 |
| amount_down | Decimal | Purchase Price × Down% |
| closing_costs | Decimal | Purchase Price × 3% |
| total_cash_down | Decimal | amount_down + closing_costs |
| loan_amount | Decimal | Purchase Price - amount_down |

### Verdict

| Field | Type | Values |
|-------|------|--------|
| verdict | str | "INVEST" \| "REVIEW" \| "PASS" |
| reasons | list[str] | Exactly 3 reasons |
| scores | dict | {cap_rate: "green"\|"yellow"\|"red", dscr: ..., coc: ..., breakeven: ...} |

### Metric Thresholds (configurable)

| Metric | Green | Yellow | Red |
|--------|-------|--------|-----|
| Cap Rate | ≥ 6% | 4-6% | < 4% |
| Cash-on-Cash | ≥ 8% | 4-8% | < 4% |
| DSCR | ≥ 1.25× | 1.0-1.25× | < 1.0× |
| Break-Even Occ | < 75% | 75-85% | > 85% |

### State Data

| State | Tax Rate | Insurance Rate |
|-------|----------|----------------|
| AZ | 0.62% | 0.50% |
| CA | 1.25% | 1.25% |
| IN | 1.37% | 0.50% |
| NV | 0.65% | 0.50% |
| TX | 1.70% | 0.50% |
| MI | 3.21% | 0.50% |

### PortfolioEntry (Google Sheet row)

Columns A-U: PropertyData (existing 15 fields + Analyze + Investible + Cashflow + Notes + 2 dead cols)
Columns V-AA: CalculationResult subset (CoC, DSCR, Price/Unit, Break-Even, Verdict, Analyze URL)
