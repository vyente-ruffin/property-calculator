"""Tests for backend.data.states — T006."""

from decimal import Decimal

import pytest

from backend.data.states import STATE_DATA, get_state_rates

EXPECTED_RATES = {
    "AZ": {"tax_rate": Decimal("0.0062"), "insurance_rate": Decimal("0.0050")},
    "CA": {"tax_rate": Decimal("0.0125"), "insurance_rate": Decimal("0.0125")},
    "IN": {"tax_rate": Decimal("0.0137"), "insurance_rate": Decimal("0.0050")},
    "NV": {"tax_rate": Decimal("0.0065"), "insurance_rate": Decimal("0.0050")},
    "TX": {"tax_rate": Decimal("0.0170"), "insurance_rate": Decimal("0.0050")},
    "MI": {"tax_rate": Decimal("0.0321"), "insurance_rate": Decimal("0.0050")},
}


class TestStateData:
    """Verify STATE_DATA contains all 6 states with correct rates."""

    def test_all_six_states_present(self):
        assert set(EXPECTED_RATES.keys()) == set(STATE_DATA.keys())

    @pytest.mark.parametrize("abbrev", EXPECTED_RATES.keys())
    def test_tax_rate(self, abbrev):
        assert STATE_DATA[abbrev]["tax_rate"] == EXPECTED_RATES[abbrev]["tax_rate"]

    @pytest.mark.parametrize("abbrev", EXPECTED_RATES.keys())
    def test_insurance_rate(self, abbrev):
        assert STATE_DATA[abbrev]["insurance_rate"] == EXPECTED_RATES[abbrev]["insurance_rate"]


class TestGetStateRates:
    """Verify get_state_rates returns correct dict or raises ValueError."""

    @pytest.mark.parametrize("abbrev", EXPECTED_RATES.keys())
    def test_returns_correct_rates(self, abbrev):
        rates = get_state_rates(abbrev)
        assert rates["tax_rate"] == EXPECTED_RATES[abbrev]["tax_rate"]
        assert rates["insurance_rate"] == EXPECTED_RATES[abbrev]["insurance_rate"]

    def test_unknown_state_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown state"):
            get_state_rates("XX")

    def test_case_insensitive_lookup(self):
        """get_state_rates should accept lowercase abbreviations."""
        rates = get_state_rates("ca")
        assert rates["tax_rate"] == Decimal("0.0125")

    def test_rates_are_decimal(self):
        rates = get_state_rates("AZ")
        assert isinstance(rates["tax_rate"], Decimal)
        assert isinstance(rates["insurance_rate"], Decimal)
