"""Tests for field mapper — T013.

Strict TDD: tests written FIRST, then backend/services/field_mapper.py.
Validates mapping from parsed PropertyData display-dict → CalculatorInput.
"""

from __future__ import annotations

from decimal import Decimal

from backend.schemas.calculator import CalculatorInput
from backend.services.field_mapper import map_property_to_input

# ── Currency parsing ────────────────────────────────────────────


class TestCurrencyParsing:
    """Strip '$' and ',' from currency strings, convert to Decimal."""

    def test_price_strips_dollar_and_commas(self):
        data = {"Price": "$1,970,000"}
        result = map_property_to_input(data)
        assert result.purchase_price == Decimal("1970000")

    def test_noi_strips_dollar_and_commas(self):
        data = {"NOI": "$106,548"}
        result = map_property_to_input(data)
        assert result.annual_noi_listing == Decimal("106548")

    def test_annual_rent_projected(self):
        data = {"Annual Rent Income (Projected)": "$152,195"}
        result = map_property_to_input(data)
        assert result.annual_gross_rents == Decimal("152195")

    def test_plain_number_without_dollar(self):
        data = {"Price": "500000"}
        result = map_property_to_input(data)
        assert result.purchase_price == Decimal("500000")

    def test_monthly_rent_from_projected(self):
        data = {"Monthly Rental Income (Projected)": "$12,683"}
        result = map_property_to_input(data)
        assert result.monthly_rent == Decimal("12683")


# ── State extraction ────────────────────────────────────────────


class TestStateExtraction:
    """Extract 2-letter state from 'City, ST ZIP' format."""

    def test_city_state_zip(self):
        data = {"City": "San Pedro, CA 90731"}
        result = map_property_to_input(data)
        assert result.state == "CA"

    def test_city_state_only(self):
        data = {"City": "Austin, TX"}
        result = map_property_to_input(data)
        assert result.state == "TX"

    def test_city_state_zip_extended(self):
        data = {"City": "Phoenix, AZ 85001-1234"}
        result = map_property_to_input(data)
        assert result.state == "AZ"


# ── Direct field mapping ────────────────────────────────────────


class TestDirectMapping:
    """Verify 1:1 field mappings."""

    def test_total_units(self):
        data = {"Total Units": 8}
        result = map_property_to_input(data)
        assert result.total_units == 8

    def test_link_to_property_url(self):
        data = {"Link": "https://example.com/listing/12345"}
        result = map_property_to_input(data)
        assert result.property_url == "https://example.com/listing/12345"


# ── Property type detection ─────────────────────────────────────


class TestPropertyTypeDetection:
    """Detect Commercial vs Residential based on Total Units."""

    def test_units_above_4_is_commercial(self):
        data = {"Total Units": 8}
        result = map_property_to_input(data)
        assert result.property_type == "Commercial"

    def test_units_equal_5_is_commercial(self):
        data = {"Total Units": 5}
        result = map_property_to_input(data)
        assert result.property_type == "Commercial"

    def test_units_equal_4_is_residential(self):
        data = {"Total Units": 4}
        result = map_property_to_input(data)
        assert result.property_type == "Residential"

    def test_units_equal_1_is_residential(self):
        data = {"Total Units": 1}
        result = map_property_to_input(data)
        assert result.property_type == "Residential"

    def test_missing_units_is_residential(self):
        data = {}
        result = map_property_to_input(data)
        assert result.property_type == "Residential"


# ── Missing / None field handling ───────────────────────────────


class TestMissingFields:
    """Missing or None fields should fall back to CalculatorInput defaults."""

    def test_empty_dict_uses_defaults(self):
        result = map_property_to_input({})
        defaults = CalculatorInput()
        assert result.down_payment_pct == defaults.down_payment_pct
        assert result.interest_rate == defaults.interest_rate
        assert result.loan_years == defaults.loan_years

    def test_none_price_uses_default(self):
        data = {"Price": None}
        result = map_property_to_input(data)
        assert result.purchase_price == CalculatorInput().purchase_price

    def test_none_noi_uses_default(self):
        data = {"NOI": None}
        result = map_property_to_input(data)
        assert result.annual_noi_listing == CalculatorInput().annual_noi_listing

    def test_none_city_uses_default_state(self):
        data = {"City": None}
        result = map_property_to_input(data)
        assert result.state == CalculatorInput().state

    def test_none_link_uses_empty_string(self):
        data = {"Link": None}
        result = map_property_to_input(data)
        assert result.property_url == ""

    def test_none_total_units_uses_default(self):
        data = {"Total Units": None}
        result = map_property_to_input(data)
        defaults = CalculatorInput()
        assert result.total_units == defaults.total_units


# ── Full integration: sample property data ──────────────────────


class TestFullMapping:
    """End-to-end mapping with the sample fixture from conftest."""

    def test_full_property_mapping(self, sample_property_data):
        result = map_property_to_input(sample_property_data)

        assert result.purchase_price == Decimal("1970000")
        assert result.state == "CA"
        assert result.annual_noi_listing == Decimal("106548")
        assert result.annual_gross_rents == Decimal("152195")
        assert result.total_units == 8
        assert result.property_url == "https://example.com/listing"
        assert result.property_type == "Commercial"
        assert result.monthly_rent == Decimal("12683")

    def test_returns_calculator_input(self, sample_property_data):
        result = map_property_to_input(sample_property_data)
        assert isinstance(result, CalculatorInput)
