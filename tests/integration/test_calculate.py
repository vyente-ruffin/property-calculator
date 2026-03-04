"""Integration tests for POST /calculate endpoint — T014.

These tests are written FIRST (TDD). They will FAIL until the
/calculate route is implemented in T022.
"""

from __future__ import annotations

# ── Commercial form submission ──────────────────────────────────


class TestCalculateCommercial:
    """POST /calculate with commercial form data."""

    FORM_DATA = {
        "property_type": "Commercial",
        "purchase_price": "1970000",
        "down_payment_pct": "30",
        "interest_rate": "6.5",
        "loan_years": "25",
        "annual_gross_rents": "152195",
        "annual_noi_listing": "106548",
        "vacancy_rate": "3",
        "other_expenses": "5000",
        "state": "CA",
        "total_units": "8",
    }

    def test_returns_html_with_verdict(self, client):
        response = client.post("/calculate", data=self.FORM_DATA)
        assert response.status_code == 200
        assert "verdict" in response.text

    def test_returns_metric_cards(self, client):
        response = client.post("/calculate", data=self.FORM_DATA)
        assert response.status_code == 200
        assert "metric" in response.text.lower() or "card" in response.text.lower() or "stat" in response.text.lower()

    def test_response_is_fragment(self, client):
        """HTMX partial — should NOT contain full document tags."""
        response = client.post("/calculate", data=self.FORM_DATA)
        assert response.status_code == 200
        text = response.text.lower()
        assert "<html" not in text
        assert "<head" not in text
        assert "<body" not in text


# ── Residential form submission ─────────────────────────────────


class TestCalculateResidential:
    """POST /calculate with residential form data."""

    FORM_DATA = {
        "property_type": "Residential",
        "purchase_price": "650000",
        "down_payment_pct": "20",
        "interest_rate": "6.5",
        "loan_years": "15",
        "monthly_rent": "5000",
        "state": "CA",
        "total_units": "1",
    }

    def test_returns_residential_content(self, client):
        response = client.post("/calculate", data=self.FORM_DATA)
        assert response.status_code == 200
        # Should contain residential-specific content (occupancy scenarios, etc.)
        text = response.text.lower()
        assert "residential" in text or "occupancy" in text or "monthly" in text
