## Development Guidelines

- Always use your context7 mcp server for all documentation to confirm your assumptions
- Always use venv to test
- Always test before telling me anything

## Networking

- **Port:** `9173` — server runs on this port, do not change without documenting
- **Bind:** Always `0.0.0.0`, never `127.0.0.1` or `localhost`
- **Access:** User tests from a separate VM — always provide the private IP URL (`http://<private-ip>:9173`)
- **Never** use ports 8080, 8090, or other common defaults (conflict with Docker/other services)
- **Never** reference `localhost` in URLs, instructions, or test commands

## Testing Guidelines

- Before saying something works, test using MCP tools:
  - Browser interactions: 
    - `browser_close`
    - `browser_resize`
    - `browser_console_messages`
    - `browser_handle_dialog`
    - `browser_evaluate`
    - `browser_file_upload`
    - `browser_install`
    - `browser_press_key`
    - `browser_type`
    - `browser_navigate`
    - `browser_navigate_back`
    - `browser_navigate_forward`
    - `browser_network_requests`
    - `browser_take_screenshot`
    - `browser_snapshot`
    - `browser_click`
    - `browser_drag`
    - `browser_hover`
    - `browser_select_option`
    - `browser_tab_list`
    - `browser_tab_new`
    - `browser_tab_select`
    - `browser_tab_close`
    - `browser_wait_for`
  - Puppeteer tools:
    - `puppeteer_navigate`
    - `puppeteer_screenshot`
    - `puppeteer_click`
    - `puppeteer_fill`
    - `puppeteer_select`
    - `puppeteer_hover`
    - `puppeteer_evaluate`

## Logging

Logging is centralized and managed externally. Do not create, modify, or replace the logger.
The `src/core/` directory is read-only — it is deployed and updated by `/init-logger` from
a shared standard. All logging in this project goes through this one interface.

- **Service name:** property-calculator
- **Mode:** Local (JSON lines to `.logs/app.log` + console)
- **Standard:** `.claude/skills/logging/SKILL.md`

### Rules

- ALL logging uses `get_logger()` — no exceptions
- NEVER use `print()`, `logging.basicConfig()`, `logging.getLogger()`, or `console.log()`
- NEVER modify or recreate anything in `src/core/` — it is read-only
- NEVER build a custom logger, logging wrapper, or logging utility
- Import the logger BEFORE importing FastAPI, Flask, or other frameworks

### How to Log (Python)

```python
from src.core.logger import get_logger

logger = get_logger(__name__)

# Standard log levels
logger.info("order created")
logger.warning("cache miss, falling back to DB")
logger.error("payment failed", exc_info=True)

# Structured data — use OTel semantic convention names
logger.info("order shipped", extra={"enduser.id": user_id, "order_id": "abc-123"})
logger.error("db timeout", exc_info=True, extra={"db.system": "postgresql"})
```

Every module gets its own logger via `get_logger(__name__)`. The logger handles formatting,
routing, and output automatically. There is nothing else to configure.