"""Google Sheets integration for the property pipeline."""

import json
from typing import Any

import gspread

from backend.config import settings


class SheetsNotConfiguredError(Exception):
    """Raised when Google Sheets credentials are not available."""

    pass


class SheetsService:
    def __init__(self):
        sa_json = settings.GOOGLE_SERVICE_ACCOUNT
        if not sa_json or sa_json == "{}":
            raise SheetsNotConfiguredError("GOOGLE_SERVICE_ACCOUNT not configured")
        creds = json.loads(sa_json)
        gc = gspread.service_account_from_dict(creds)
        self._sheet = gc.open_by_key(settings.GOOGLE_SHEET_ID)
        self._worksheet = self._sheet.sheet1

    def get_all_properties(self) -> list[dict[str, Any]]:
        """Read all rows as list of dicts (header row = keys)."""
        return self._worksheet.get_all_records()

    def append_property(self, data: dict[str, Any]) -> int:
        """Append a row and return the new row number."""
        headers = self._worksheet.row_values(1)
        row = [str(data.get(h, "")) for h in headers]
        self._worksheet.append_row(row, value_input_option="USER_ENTERED")
        return self._worksheet.row_count

    def get_summary(self) -> dict[str, Any]:
        """Get portfolio summary stats."""
        records = self.get_all_properties()
        good = sum(1 for r in records if "GOOD" in str(r.get("Investible", "")))
        bad = sum(1 for r in records if "BAD" in str(r.get("Investible", "")))
        return {
            "total_deals": len(records),
            "good_deals": good,
            "bad_deals": bad,
        }
