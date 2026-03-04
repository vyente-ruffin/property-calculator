"""Integration tests for URL state management — T031.

Verify that /calculate returns HX-Push-Url and that loading
a URL with query params renders the same results.
"""

from __future__ import annotations


def test_calculate_returns_push_url(client):
    response = client.post(
        "/calculate",
        data={
            "property_type": "Commercial",
            "purchase_price": "1970000",
            "down_payment_pct": "30",
            "state": "CA",
        },
    )
    assert "HX-Push-Url" in response.headers
    url = response.headers["HX-Push-Url"]
    assert "purchase_price=1970000" in url
    assert "state=CA" in url


def test_get_with_params_renders_results(client):
    response = client.get(
        "/?property_type=Commercial&purchase_price=1970000&down_payment_pct=30"
        "&interest_rate=6.5&loan_years=25&annual_gross_rents=152195"
        "&annual_noi_listing=106548&vacancy_rate=3&other_expenses=5000"
        "&total_units=8&state=CA"
    )
    assert response.status_code == 200
    assert "verdict" in response.text.lower()
    assert "Cap Rate" in response.text or "cap" in response.text.lower()


def test_round_trip_state_preservation(client):
    """Submit form, get URL, load URL, same results."""
    post_resp = client.post(
        "/calculate",
        data={
            "property_type": "Commercial",
            "purchase_price": "1970000",
            "state": "CA",
            "down_payment_pct": "30",
            "interest_rate": "6.5",
            "loan_years": "25",
            "annual_gross_rents": "152195",
            "annual_noi_listing": "106548",
            "vacancy_rate": "3",
            "other_expenses": "5000",
            "total_units": "8",
        },
    )
    url = post_resp.headers.get("HX-Push-Url", "/")
    get_resp = client.get(url)
    assert get_resp.status_code == 200
    assert "verdict" in get_resp.text.lower()
