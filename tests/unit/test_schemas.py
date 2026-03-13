"""Tests for backend.schemas.calculator — T010."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.schemas.calculator import CalculationResult, CalculatorInput


class TestCalculatorInputDefaults:
    """Verify all default values match the spec."""

    def test_defaults(self):
        inp = CalculatorInput()
        assert inp.property_type == "Commercial"
        assert inp.purchase_price == Decimal("1970000")
        assert inp.down_payment_pct == Decimal("30")
        assert inp.interest_rate == Decimal("6.5")
        assert inp.loan_years == 25
        assert inp.total_units == 8
        assert inp.state == "CA"
        assert inp.property_url == ""
        # Commercial-specific
        assert inp.annual_gross_rents == Decimal("152195")
        assert inp.annual_noi_listing == Decimal("106548")
        assert inp.vacancy_rate == Decimal("3")
        assert inp.other_expenses == Decimal("5000")
        # Residential-specific
        assert inp.monthly_rent == Decimal("5000")


class TestCalculatorInputValidation:
    """Verify range constraints reject bad values."""

    def test_down_payment_pct_too_low(self):
        with pytest.raises(ValidationError):
            CalculatorInput(down_payment_pct=Decimal("-1"))

    def test_down_payment_pct_too_high(self):
        with pytest.raises(ValidationError):
            CalculatorInput(down_payment_pct=Decimal("101"))

    def test_down_payment_pct_boundary_zero(self):
        inp = CalculatorInput(down_payment_pct=Decimal("0"))
        assert inp.down_payment_pct == Decimal("0")

    def test_down_payment_pct_boundary_100(self):
        inp = CalculatorInput(down_payment_pct=Decimal("100"))
        assert inp.down_payment_pct == Decimal("100")

    def test_interest_rate_too_low(self):
        with pytest.raises(ValidationError):
            CalculatorInput(interest_rate=Decimal("-0.1"))

    def test_interest_rate_too_high(self):
        with pytest.raises(ValidationError):
            CalculatorInput(interest_rate=Decimal("21"))

    def test_interest_rate_boundary_zero(self):
        inp = CalculatorInput(interest_rate=Decimal("0"))
        assert inp.interest_rate == Decimal("0")

    def test_interest_rate_boundary_20(self):
        inp = CalculatorInput(interest_rate=Decimal("20"))
        assert inp.interest_rate == Decimal("20")

    def test_loan_years_too_low(self):
        with pytest.raises(ValidationError):
            CalculatorInput(loan_years=0)

    def test_loan_years_too_high(self):
        with pytest.raises(ValidationError):
            CalculatorInput(loan_years=31)

    def test_total_units_too_low(self):
        with pytest.raises(ValidationError):
            CalculatorInput(total_units=0)

    def test_vacancy_rate_too_low(self):
        with pytest.raises(ValidationError):
            CalculatorInput(vacancy_rate=Decimal("-1"))

    def test_vacancy_rate_too_high(self):
        with pytest.raises(ValidationError):
            CalculatorInput(vacancy_rate=Decimal("51"))

    def test_vacancy_rate_boundary_zero(self):
        inp = CalculatorInput(vacancy_rate=Decimal("0"))
        assert inp.vacancy_rate == Decimal("0")

    def test_vacancy_rate_boundary_50(self):
        inp = CalculatorInput(vacancy_rate=Decimal("50"))
        assert inp.vacancy_rate == Decimal("50")


class TestCalculatorInputSerialization:
    """Verify CalculatorInput can round-trip through JSON."""

    def test_json_round_trip(self):
        inp = CalculatorInput()
        data = inp.model_dump()
        restored = CalculatorInput(**data)
        assert restored.purchase_price == inp.purchase_price


class TestCalculationResult:
    """Verify CalculationResult can be instantiated with sample data."""

    def _sample_data(self) -> dict:
        return {
            "noi_estimated": Decimal("100000"),
            "noi_listing": Decimal("106548"),
            "noi_delta_pct": Decimal("-6.15"),
            "cap_rate": Decimal("5.08"),
            "cash_on_cash": Decimal("3.20"),
            "dscr": Decimal("1.15"),
            "price_per_unit": Decimal("246250"),
            "breakeven_occ": Decimal("82.5"),
            "grm": Decimal("12.95"),
            "annual_cash_flow": Decimal("18900"),
            "monthly_payment": Decimal("9300"),
            "annual_debt_service": Decimal("111600"),
            "amount_down": Decimal("591000"),
            "closing_costs": Decimal("19700"),
            "total_cash_down": Decimal("610700"),
            "loan_amount": Decimal("1379000"),
        }

    def test_creation(self):
        result = CalculationResult(**self._sample_data())
        assert result.cap_rate == Decimal("5.08")
        assert result.loan_amount == Decimal("1379000")

    def test_all_fields_present(self):
        result = CalculationResult(**self._sample_data())
        expected_fields = {
            "noi_estimated", "noi_listing", "noi_delta_pct", "cap_rate",
            "cash_on_cash", "dscr", "price_per_unit", "breakeven_occ",
            "grm", "annual_cash_flow", "monthly_payment", "annual_debt_service",
            "amount_down", "closing_costs", "total_cash_down", "loan_amount",
        }
        actual = set(result.__class__.model_fields.keys())
        assert expected_fields.issubset(actual)

    def test_serialization(self):
        result = CalculationResult(**self._sample_data())
        data = result.model_dump() if hasattr(result, "model_dump") else vars(result)
        assert "cap_rate" in data
        assert data["cap_rate"] == Decimal("5.08")
