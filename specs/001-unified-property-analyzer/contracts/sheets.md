# Contract: Google Sheets Endpoints

## GET /api/properties

### Request
- **Method**: GET
- **Query Params** (optional): `?limit=50&sort=date_desc`

### Response
```json
{
  "properties": [
    {
      "row_number": 2,
      "Price": "$1,970,000",
      "Address": "252 W 11th St",
      "City": "San Pedro, CA 90731",
      "Cap Rate": "5.46%",
      "Total Units": 8,
      "Investible": "✅ GOOD",
      "Cashflow": "$8,391",
      "Cash_on_Cash": "6.2%",
      "DSCR": "1.18",
      "Verdict": "REVIEW",
      "Analyze_URL": "/?property_type=Commercial&purchase_price=1970000&..."
    }
  ],
  "total": 235,
  "summary": {
    "total_deals": 235,
    "good_deals": 65,
    "bad_deals": 170,
    "avg_cashflow": -15510
  }
}
```

## POST /api/properties

### Request
```json
{
  "Price": "$1,970,000",
  "Address": "252 W 11th St",
  "City": "San Pedro, CA 90731",
  "Cap Rate": "5.46%",
  "Date On Market": "2026-03-04",
  "Monthly Rental Income (Projected)": "$12,683",
  "Monthly Rental Income (Actual)": "",
  "Annual Rent Income (Projected)": "$152,195",
  "Annual Rent Income (Actual)": "",
  "NOI": "$106,548",
  "Lot / building size": "6,500 SF / 5,876 SF",
  "Total Units": 8,
  "Unit Mix Summary": "2×3BD/2BA@$2,100 | 4×2BD/1BA@$1,650 | 2×1BD/1BA@$1,300",
  "Link": "https://example.com/listing",
  "Description": "Eight-unit multifamily in San Pedro...",
  "Analyze": "Analyze",
  "Investible": "⚠️ REVIEW",
  "Cashflow": "$8,391",
  "Notes": "",
  "Monthly Rental Income": "",
  "Annual Rent Income": "",
  "Cash_on_Cash": "6.2%",
  "DSCR": "1.18",
  "Price_per_Unit": "$246,250",
  "Break_Even_Occ": "79%",
  "Verdict": "REVIEW",
  "Analyze_URL": "/?property_type=Commercial&purchase_price=1970000&..."
}
```

### Response
```json
{
  "status": "saved",
  "row": 237
}
```

### Error Response
```json
{
  "status": "error",
  "message": "Google Sheets API error: insufficient permissions"
}
```

## Authentication
- Server-side only: `GOOGLE_SERVICE_ACCOUNT` env variable (JSON string)
- `gspread.service_account_from_dict(json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT']))`
- Sheet must be shared with service account email address

## Sheet Details
- Spreadsheet ID: `1dVf1UShQry4nDvM3HbqM9ts0ltbKnruEDKd6lZ_xAMg`
- Tab: "PropertiesForSale" (gid=0)
- Columns A-U: existing (preserve)
- Columns V-AA: new calculated fields
