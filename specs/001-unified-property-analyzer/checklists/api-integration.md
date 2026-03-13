# API & Integration Checklist: Unified Property Analyzer

**Purpose**: Validate all API endpoints, SSE streaming, Google Sheets integration, and data flow
**Created**: 2026-03-04
**Feature**: [spec.md](../spec.md) — Principles II, V

## POST /calculate

- [ ] CHK078 Accepts form-encoded data (application/x-www-form-urlencoded)
- [ ] CHK079 Returns HTML fragment (NOT full page — no `<html>`, `<head>`, `<body>` tags)
- [ ] CHK080 Returns correct Content-Type: text/html
- [ ] CHK081 Sets HX-Push-Url response header with all form params
- [ ] CHK082 Handles missing optional fields by using defaults (not crashing)
- [ ] CHK083 Handles invalid numeric input (non-numeric string) with error message
- [ ] CHK084 Responds in <100ms for typical input (no external API calls)
- [ ] CHK085 Commercial and Residential return different result structures
- [ ] CHK086 Verdict banner included in response with correct color class

## POST /api/parse (existing — verify preservation)

- [ ] CHK087 Accepts JSON `{"text": "..."}` body
- [ ] CHK088 Returns Content-Type: text/event-stream
- [ ] CHK089 Streams SSE events with `data: {...}\n\n` format
- [ ] CHK090 Emits events for all 7 steps: parse_input, scrape_url, extract_fields, search_link, rentcast, reextract, validate
- [ ] CHK091 Final `complete` event contains full 15-field property dict
- [ ] CHK092 Skipped steps emit `status: "skipped"` (not omitted)
- [ ] CHK093 Error in any step emits `status: "error"` with detail (not crash)
- [ ] CHK094 SSE stream closes after `complete` event

## GET /api/properties

- [ ] CHK095 Returns JSON array of property objects
- [ ] CHK096 Each object contains all 21 existing columns + 6 new columns (where populated)
- [ ] CHK097 Returns `summary` object with total_deals, good_deals, bad_deals, avg_cashflow
- [ ] CHK098 Handles empty sheet gracefully (returns empty array, not error)
- [ ] CHK099 Response time <3s for 235 rows

## POST /api/properties

- [ ] CHK100 Accepts JSON body with 27 fields (21 existing + 6 calculated)
- [ ] CHK101 Returns `{"status": "saved", "row": N}` on success
- [ ] CHK102 Appends row to end of sheet (does not overwrite existing data)
- [ ] CHK103 Uses `value_input_option="USER_ENTERED"` so currency formatting is preserved
- [ ] CHK104 Returns `{"status": "error", "message": "..."}` on Google API failure
- [ ] CHK105 Handles missing GOOGLE_SERVICE_ACCOUNT env var gracefully (503, not crash)

## Google Sheets Service

- [ ] CHK106 `service_account_from_dict()` authenticates from env var JSON string
- [ ] CHK107 Opens sheet by key `1dVf1UShQry4nDvM3HbqM9ts0ltbKnruEDKd6lZ_xAMg`
- [ ] CHK108 `get_all_records()` returns list of dicts with correct column headers
- [ ] CHK109 `append_rows()` adds row in correct column order (A through AA)
- [ ] CHK110 Service handles API rate limits gracefully (retry or queue)
- [ ] CHK111 Service handles network timeout (5s timeout, clear error message)

## SSE → Form Auto-Population

- [ ] CHK112 parse.js reads SSE stream via fetch + ReadableStream (not EventSource — POST not supported)
- [ ] CHK113 On `complete` event, maps 15 fields to calculator form inputs
- [ ] CHK114 Field mapping: Price→purchase_price, Annual Rent→annual_gross_rents, NOI→annual_noi_listing
- [ ] CHK115 State extracted from "City, ST ZIP" format (e.g., "San Pedro, CA 90731" → "CA")
- [ ] CHK116 After form population, programmatically triggers HTMX calculation (`htmx.trigger`)
- [ ] CHK117 Missing parsed fields leave form inputs at default values (not blank/NaN)

## URL State Management

- [ ] CHK118 All calculator inputs serialized as query params in URL
- [ ] CHK119 Loading URL with params pre-fills form AND renders results (not just form)
- [ ] CHK120 Changing any input updates URL in real-time via HX-Push-Url
- [ ] CHK121 URL is copy-pasteable — recipient sees identical analysis

## Notes

- API contracts are defined in `specs/001-.../contracts/`
- SSE parsing pattern already proven in existing `frontend/chat.js` — port, don't rewrite
- Google Sheets API has 60 writes/min limit — not a concern for this team size
