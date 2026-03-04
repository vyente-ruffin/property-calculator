"""T028 — Verify POST /calculate returns HTML fragment, not full page."""


def test_calculate_returns_fragment_only(client):
    """POST /calculate should return HTML fragment, not full page."""
    response = client.post(
        "/calculate",
        data={
            "property_type": "Commercial",
            "purchase_price": "1970000",
            "down_payment_pct": "30",
            "interest_rate": "6.5",
            "loan_years": "25",
            "annual_gross_rents": "152195",
            "annual_noi_listing": "106548",
            "vacancy_rate": "3",
            "other_expenses": "5000",
            "total_units": "8",
            "state": "CA",
        },
    )
    assert response.status_code == 200
    assert "<html" not in response.text.lower()
    assert "<head" not in response.text.lower()
    assert "<body" not in response.text.lower()
    assert "verdict" in response.text.lower()


def test_calculate_sets_push_url_header(client):
    """POST /calculate should set HX-Push-Url with query params."""
    response = client.post(
        "/calculate",
        data={"property_type": "Commercial", "purchase_price": "1970000"},
    )
    assert "HX-Push-Url" in response.headers
    assert "purchase_price=1970000" in response.headers["HX-Push-Url"]
