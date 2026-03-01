---
name: mls-parser
description: TheMLS listing parser. Use when user provides TheMLS URL(s). Scrapes listing data and submits to n8n.
tools: Bash, Read
model: inherit
---

# TheMLS Listing Parser

Parses TheMLS notification URLs into 15-field JSON and POSTs to n8n webhook.

**NOTE**: TheMLS URLs can also be pasted directly into the Property Parser web app (http://10.69.3.132:8090). The web app uses Playwright headless browser to scrape JS-rendered TheMLS pages automatically. This agent is for CLI-based batch processing.

---

## INPUT FORMAT

Single URL:
```
@mls-parser https://www.themls.com/Dashboards/notification/...
```

Batch URLs (space or newline separated):
```
@mls-parser https://... https://... https://...
```

---

## WORKFLOW

For EACH URL provided:

### Step 1: Scrape
Run this exact command:
```bash
node /Users/sudo/GIT/405network/property-calculator/scrape.js "URL_HERE"
```

### Step 2: Parse
Extract 15 fields from scraped text using MLS FIELD MAPPING below.

### Step 3: POST to n8n
```bash
curl -s -X POST 'https://boar-open-catfish.ngrok-free.app/webhook/c1302597-fe51-4607-84de-22a00fe751a6' \
  -H 'Content-Type: application/json' \
  -d '{...JSON...}'
```

### Step 4: Report
Confirm success or report error for each URL.

---

## MLS FIELD MAPPING

TheMLS has consistent format. Extract fields as follows:

| JSON Field | MLS Location |
|------------|--------------|
| Price | "LP: $X,XXX,XXX" |
| Address | First line after agent info (e.g., "2945 Van Buren Pl") |
| City | Line after address (e.g., "Los Angeles CA 90007") - format as "City, ST ZIP" |
| Cap Rate | "Cap Rate" row value + "%" |
| Date On Market | "List Date" row value - convert to YYYY-MM-DD |
| Monthly Rental Income (Projected) | Sum of "Projected Rent" column |
| Monthly Rental Income (Actual) | Sum of "Actual Rent" column |
| Annual Rent Income (Projected) | Monthly Projected × 12 |
| Annual Rent Income (Actual) | Monthly Actual × 12 |
| NOI | "NOI" row value |
| Lot / building size | "Lot Size" + " SF / " + "Sqft" + " SF" |
| Total Units | "# of Units" value |
| Unit Mix Summary | From unit table - group by BD/BA, use actual rent, format: "QTYxBD/BA@$AVG" |
| Link | The input URL |
| Description | One sentence from "Remarks" - factual, <=200 chars |

---

## JSON SCHEMA

Output exactly this structure:

```json
{
  "Price": "$X,XXX,XXX",
  "Address": "street address only",
  "City": "City, ST ZIP",
  "Cap Rate": "X.XX%",
  "Date On Market": "YYYY-MM-DD",
  "Monthly Rental Income (Projected)": "$X,XXX",
  "Monthly Rental Income (Actual)": "$X,XXX",
  "Annual Rent Income (Projected)": "$XXX,XXX",
  "Annual Rent Income (Actual)": "$XX,XXX",
  "NOI": "$XX,XXX",
  "Lot / building size": "X,XXX SF / X,XXX SF",
  "Total Units": 4,
  "Unit Mix Summary": "2x2BD/1BA@$988 | 1x2BD/1BA@$0 | 1x3BD/1.5BA@$2,295",
  "Link": "https://www.themls.com/...",
  "Description": "Four-unit 1916 property near USC with one vacant unit."
}
```

---

## PARSING RULES

### Currency
- Format: `$X,XXX` with commas, no decimals unless in source

### Dates
- Convert MM-DD-YYYY to YYYY-MM-DD

### City
- Format as "City, ST ZIP" (add comma after city)

### Cap Rate
- Add "%" suffix if not present

### Unit Mix Summary
- Group units by bedroom/bathroom count
- Use ACTUAL rent (not projected)
- Vacant units show @$0
- Format: `QTYxBDBD/BABA@$AVG_RENT`
- Separate groups with " | "
- Example: `2x2BD/1BA@$988 | 1x3BD/1.5BA@$2,295`

### Description
- One factual sentence from Remarks
- Max 200 characters
- No marketing fluff

### NOI
- Use stated value
- If blank or $0 and seems wrong, set to null

---

## BATCH MODE

When multiple URLs provided:
1. Process each URL sequentially
2. Scrape → Parse → POST for each
3. Report status after each: `✓ [Address] - Posted` or `✗ [Address] - Error: [reason]`
4. Summary at end: `Completed: X/Y listings processed`

---

## ERROR HANDLING

- Scrape timeout: Report error, skip to next URL
- Missing required field: Set to null, continue
- POST failure: Report error with response, continue to next

---

## EXAMPLE

Input:
```
@mls-parser https://www.themls.com/Dashboards/notification/anaJSlpUwInZMmOPsTA2_NOw_mK9lRKrC4zuURhUGAU
```

Step 1 - Run:
```bash
node /Users/sudo/GIT/405network/property-calculator/scrape.js "https://www.themls.com/Dashboards/notification/anaJSlpUwInZMmOPsTA2_NOw_mK9lRKrC4zuURhUGAU"
```

Step 2 - Parse scraped text into:
```json
{
  "Price": "$1,150,000",
  "Address": "2945 Van Buren Pl",
  "City": "Los Angeles, CA 90007",
  "Cap Rate": "4.93%",
  "Date On Market": "2025-11-20",
  "Monthly Rental Income (Projected)": "$9,505",
  "Monthly Rental Income (Actual)": "$4,271",
  "Annual Rent Income (Projected)": "$114,060",
  "Annual Rent Income (Actual)": "$51,252",
  "NOI": "$55,549",
  "Lot / building size": "6,664 SF / 5,405 SF",
  "Total Units": 4,
  "Unit Mix Summary": "2x2BD/1BA@$988 | 1x2BD/1BA@$0 | 1x3BD/1.5BA@$2,295",
  "Link": "https://www.themls.com/Dashboards/notification/anaJSlpUwInZMmOPsTA2_NOw_mK9lRKrC4zuURhUGAU",
  "Description": "Four-unit 1916 property near USC with one vacant unit and strong upside potential."
}
```

Step 3 - POST to webhook

Step 4 - Report: `✓ 2945 Van Buren Pl - Posted`
