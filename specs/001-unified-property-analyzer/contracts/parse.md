# Contract: POST /api/parse (existing — no changes)

## Request
- **Method**: POST
- **Content-Type**: application/json

```json
{
  "text": "252 W 11th St, San Pedro, CA 90731\n8-Unit Multifamily · $1,970,000\n..."
}
```

## Response
- **Content-Type**: text/event-stream
- **Cache-Control**: no-cache
- **X-Accel-Buffering**: no

### SSE Events (in order)
```
data: {"step": "parse_input", "status": "running"}
data: {"step": "parse_input", "status": "done", "data": {"text_length": 2847, "has_url": false, "is_url_only": false}}

data: {"step": "scrape_url", "status": "skipped"}

data: {"step": "extract_fields", "status": "running"}
data: {"step": "extract_fields", "status": "done", "data": {"fields": {15-field dict}}}

data: {"step": "search_link", "status": "done", "data": {"url": "https://..."}}

data: {"step": "rentcast", "status": "done", "data": {"rent": {"monthly_formatted": "$14,200"}}}

data: {"step": "reextract", "status": "done", "data": {"fields": {updated 15-field dict}}}

data: {"step": "validate", "status": "done", "data": {"valid": true, "missing_keys": [], "null_fields": []}}

data: {"step": "complete", "status": "done", "data": {"result": {final 15-field dict}}}
```

### Step Names (7 total)
1. `parse_input` — split text/URL
2. `scrape_url` — fetch page if URL-only (may be skipped)
3. `extract_fields` — Azure OpenAI structured extraction
4. `search_link` — DuckDuckGo URL search (if no link found)
5. `rentcast` — Rentcast API for projected rents
6. `reextract` — merge enrichment + re-extract
7. `validate` — check all fields present

### Frontend Consumption (NEW — parse.js)
```javascript
const eventSource = new EventSource('/api/parse', { method: 'POST' });
// Actually: fetch('/api/parse', {method: 'POST', body: JSON.stringify({text}), headers: {'Content-Type': 'application/json'}})
// Read response.body as ReadableStream, parse SSE lines
```

Note: Standard EventSource only supports GET. For POST, use fetch() with ReadableStream to parse SSE manually (same pattern as existing frontend/chat.js).
