"""Integration tests for Google Sheets service."""

import os

import pytest

from backend.services.sheets import SheetsNotConfiguredError, SheetsService

_has_creds = os.getenv("GOOGLE_SERVICE_ACCOUNT", "{}") not in ("", "{}")
_skip_reason = "GOOGLE_SERVICE_ACCOUNT not configured"


class TestSheetsNotConfiguredError:
    """Tests that run without real credentials."""

    def test_raises_when_no_credentials(self, monkeypatch):
        monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT", "{}")
        from backend.config import Settings

        monkeypatch.setattr("backend.services.sheets.settings", Settings())
        with pytest.raises(SheetsNotConfiguredError):
            SheetsService()

    def test_raises_when_empty_credentials(self, monkeypatch):
        monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT", "")
        from backend.config import Settings

        monkeypatch.setattr("backend.services.sheets.settings", Settings())
        with pytest.raises(SheetsNotConfiguredError):
            SheetsService()


@pytest.mark.skipif(not _has_creds, reason=_skip_reason)
class TestSheetsRead:
    """Tests that require real Google credentials (skipped in CI)."""

    def test_get_all_properties_returns_list_of_dicts(self):
        svc = SheetsService()
        records = svc.get_all_properties()
        assert isinstance(records, list)
        if records:
            assert isinstance(records[0], dict)

    def test_get_summary_returns_expected_keys(self):
        svc = SheetsService()
        summary = svc.get_summary()
        assert "total_deals" in summary
        assert "good_deals" in summary
        assert "bad_deals" in summary


@pytest.mark.skipif(not _has_creds, reason=_skip_reason)
class TestSheetsWrite:
    """Write tests that require real Google credentials (skipped in CI)."""

    def test_append_property_adds_row(self):
        svc = SheetsService()
        headers = svc._worksheet.row_values(1)
        test_data = {h: f"TEST_{h}" for h in headers}
        row_num = svc.append_property(test_data)
        assert isinstance(row_num, int)
        assert row_num > 1
