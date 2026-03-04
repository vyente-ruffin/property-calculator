"""Shared test fixtures for the Property Analyzer test suite."""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def sample_commercial_input():
    """Standard commercial test case — validated against Excel reference."""
    return {
        "property_type": "Commercial",
        "purchase_price": Decimal("1970000"),
        "down_payment_pct": Decimal("30"),
        "annual_gross_rents": Decimal("152195"),
        "annual_noi_listing": Decimal("106548"),
        "vacancy_rate": Decimal("3"),
        "other_expenses": Decimal("5000"),
        "interest_rate": Decimal("6.5"),
        "loan_years": 25,
        "total_units": 8,
        "state": "CA",
        "property_url": "",
    }


@pytest.fixture
def sample_residential_input():
    """Standard residential test case — validated against Excel reference."""
    return {
        "property_type": "Residential",
        "purchase_price": Decimal("650000"),
        "down_payment_pct": Decimal("20"),
        "interest_rate": Decimal("6.5"),
        "loan_years": 15,
        "monthly_rent": Decimal("5000"),
        "state": "CA",
        "property_url": "",
    }


@pytest.fixture
def sample_property_data():
    """Sample parsed PropertyData from the parser pipeline."""
    return {
        "Price": "$1,970,000",
        "Address": "252 W 11th St",
        "City": "San Pedro, CA 90731",
        "Cap Rate": "5.46%",
        "Date On Market": "2026-03-04",
        "Monthly Rental Income (Projected)": "$12,683",
        "Monthly Rental Income (Actual)": None,
        "Annual Rent Income (Projected)": "$152,195",
        "Annual Rent Income (Actual)": None,
        "NOI": "$106,548",
        "Lot / building size": "6,500 SF / 5,876 SF",
        "Total Units": 8,
        "Unit Mix Summary": "2×3BD/2BA@$2,100 | 4×2BD/1BA@$1,650 | 2×1BD/1BA@$1,300",
        "Link": "https://example.com/listing",
        "Description": "Eight-unit multifamily in San Pedro",
        "Image_URL": None,
    }


@pytest.fixture
def client():
    """FastAPI TestClient for integration tests."""
    from server import app
    return TestClient(app)
