"""Integration tests for OG meta tags — T048.

Verify dynamic Open Graph tags render correctly with and without
calculator params in the URL.
"""

from __future__ import annotations


def test_og_tags_with_params(client):
    response = client.get(
        "/?purchase_price=1970000&property_type=Commercial&total_units=8"
    )
    assert "og:title" in response.text
    assert "1,970,000" in response.text or "1970000" in response.text


def test_og_tags_without_params(client):
    response = client.get("/")
    assert "og:title" in response.text
    assert "Property Analyzer" in response.text


def test_og_description_with_metrics(client):
    response = client.get(
        "/?property_type=Commercial&purchase_price=1970000&down_payment_pct=30"
        "&interest_rate=6.5&loan_years=25&annual_gross_rents=152195"
        "&annual_noi_listing=106548&vacancy_rate=3&other_expenses=5000"
        "&total_units=8&state=CA"
    )
    assert "og:description" in response.text
