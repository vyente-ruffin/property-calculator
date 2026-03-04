# Contract: POST /calculate

## Request
- **Method**: POST
- **Content-Type**: application/x-www-form-urlencoded (HTMX form submission)
- **Source**: `hx-post="/calculate"` on sidebar form inputs

### Form Fields (Commercial)
```
property_type=Commercial
purchase_price=1970000
down_payment_pct=30
annual_gross_rents=152195
annual_noi_listing=106548
vacancy_rate=3
other_expenses=5000
interest_rate=6.5
loan_years=25
total_units=8
state=CA
property_url=https://example.com/listing
```

### Form Fields (Residential)
```
property_type=Residential
purchase_price=650000
down_payment_pct=20
interest_rate=6.5
loan_years=15
monthly_rent=5000
state=CA
property_url=https://example.com/listing
```

## Response
- **Content-Type**: text/html (Jinja2 partial)
- **Template**: `partials/results_overview.html`
- **HTMX Header**: `HX-Push-Url: /?property_type=Commercial&purchase_price=1970000&...`

### Response contains:
1. Verdict banner (INVEST/REVIEW/PASS + 3 reasons)
2. 4 primary metric cards (Cap Rate, CoC, DSCR, NOI)
3. 3 secondary metric cards (Price/Unit, Break-Even, GRM)
4. NOI comparison (broker vs estimated with delta %)
5. Operating expenses table (monthly + annual)
6. Investment analysis table
7. Investment summary grid

## Error Handling
- Invalid numeric input → return partial with error message in verdict area
- Missing required field → use defaults, show warning indicator
