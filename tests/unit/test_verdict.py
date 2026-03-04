"""Tests for backend.services.verdict — T009 Verdict Engine."""

from decimal import Decimal

import pytest

from backend.schemas.calculator import CalculationResult  # noqa: F401 — used in _make_result
from backend.services.verdict import generate_verdict


def _make_result(
    *,
    cap_rate: str = "7.0",
    cash_on_cash: str = "9.0",
    dscr: str = "1.5",
    breakeven_occ: str = "70",
) -> CalculationResult:
    """Build a CalculationResult with sensible defaults, overriding key metrics."""
    return CalculationResult(
        noi_estimated=Decimal("100000"),
        noi_listing=Decimal("100000"),
        noi_delta_pct=Decimal("0"),
        cap_rate=Decimal(cap_rate),
        cash_on_cash=Decimal(cash_on_cash),
        dscr=Decimal(dscr),
        price_per_unit=Decimal("250000"),
        breakeven_occ=Decimal(breakeven_occ),
        grm=Decimal("10"),
        annual_cash_flow=Decimal("50000"),
        monthly_payment=Decimal("5000"),
        annual_debt_service=Decimal("60000"),
        amount_down=Decimal("500000"),
        closing_costs=Decimal("20000"),
        total_cash_down=Decimal("520000"),
        loan_amount=Decimal("1500000"),
    )


class TestInvest:
    """All 4 metrics green → INVEST."""

    def test_verdict_is_invest(self):
        result = _make_result(cap_rate="7.0", cash_on_cash="9.0", dscr="1.5", breakeven_occ="70")
        v = generate_verdict(result)
        assert v.verdict == "INVEST"

    def test_exactly_3_reasons(self):
        v = generate_verdict(_make_result())
        assert len(v.reasons) == 3

    def test_all_scores_green(self):
        v = generate_verdict(_make_result())
        assert all(s == "green" for s in v.scores.values())


class TestPassRedMetric:
    """Any single metric red → PASS."""

    def test_dscr_red_forces_pass(self):
        v = generate_verdict(_make_result(dscr="0.8"))
        assert v.verdict == "PASS"

    def test_cap_rate_red_forces_pass(self):
        v = generate_verdict(_make_result(cap_rate="3.0"))
        assert v.verdict == "PASS"

    def test_coc_red_forces_pass(self):
        v = generate_verdict(_make_result(cash_on_cash="2.0"))
        assert v.verdict == "PASS"

    def test_breakeven_red_forces_pass(self):
        v = generate_verdict(_make_result(breakeven_occ="90"))
        assert v.verdict == "PASS"

    def test_reasons_mention_red_metric(self):
        v = generate_verdict(_make_result(dscr="0.8"))
        combined = " ".join(v.reasons)
        assert "DSCR" in combined or "dscr" in combined.lower()


class TestPassDSCRBelowOne:
    """DSCR < 1.0 always forces PASS even when score is yellow."""

    def test_dscr_095_forces_pass(self):
        # DSCR 0.95 scores "red" (<1.0 threshold), so this is PASS
        v = generate_verdict(_make_result(dscr="0.95"))
        assert v.verdict == "PASS"

    def test_dscr_099_forces_pass(self):
        v = generate_verdict(_make_result(dscr="0.99"))
        assert v.verdict == "PASS"


class TestReview:
    """Mixed green+yellow, no red → REVIEW."""

    def test_verdict_is_review(self):
        v = generate_verdict(
            _make_result(cap_rate="5.5", cash_on_cash="6.0", dscr="1.15", breakeven_occ="78")
        )
        assert v.verdict == "REVIEW"

    def test_review_exactly_3_reasons(self):
        v = generate_verdict(
            _make_result(cap_rate="5.5", cash_on_cash="6.0", dscr="1.15", breakeven_occ="78")
        )
        assert len(v.reasons) == 3


class TestReasonCount:
    """Every verdict returns exactly 3 reason strings."""

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"cap_rate": "7.0", "cash_on_cash": "9.0", "dscr": "1.5", "breakeven_occ": "70"},
            {"dscr": "0.8"},
            {"cap_rate": "5.5", "cash_on_cash": "6.0", "dscr": "1.15", "breakeven_occ": "78"},
            {"cap_rate": "3.0", "cash_on_cash": "2.0", "dscr": "0.5", "breakeven_occ": "95"},
        ],
    )
    def test_always_3_reasons(self, kwargs):
        v = generate_verdict(_make_result(**kwargs))
        assert isinstance(v.reasons, list)
        assert len(v.reasons) == 3
        assert all(isinstance(r, str) for r in v.reasons)


class TestReasonsContainValues:
    """Each reason string mentions the actual metric value."""

    def test_invest_reasons_contain_values(self):
        v = generate_verdict(_make_result(cap_rate="7.0", cash_on_cash="9.0", dscr="1.5", breakeven_occ="70"))
        combined = " ".join(v.reasons)
        # With 4 green metrics and only 3 reason slots, at least 3 values appear
        found = sum(1 for val in ("7.0", "9.0", "1.5", "70") if val in combined)
        assert found >= 3

    def test_pass_reasons_mention_failing_value(self):
        v = generate_verdict(_make_result(dscr="0.8"))
        combined = " ".join(v.reasons)
        assert "0.8" in combined or "0.80" in combined

    def test_review_reasons_mention_values(self):
        v = generate_verdict(
            _make_result(cap_rate="5.5", cash_on_cash="6.0", dscr="1.15", breakeven_occ="78")
        )
        combined = " ".join(v.reasons)
        # At least one metric value should appear
        has_value = any(val in combined for val in ("5.5", "6.0", "1.15", "78"))
        assert has_value


class TestScoresDict:
    """Returns dict with keys cap_rate, coc, dscr, breakeven → green/yellow/red."""

    def test_all_green(self):
        v = generate_verdict(_make_result())
        assert v.scores == {
            "cap_rate": "green",
            "coc": "green",
            "dscr": "green",
            "breakeven": "green",
        }

    def test_mixed_scores(self):
        v = generate_verdict(
            _make_result(cap_rate="5.5", cash_on_cash="6.0", dscr="1.15", breakeven_occ="78")
        )
        assert v.scores["cap_rate"] == "yellow"
        assert v.scores["coc"] == "yellow"
        assert v.scores["dscr"] == "yellow"
        assert v.scores["breakeven"] == "yellow"

    def test_has_all_keys(self):
        v = generate_verdict(_make_result())
        assert set(v.scores.keys()) == {"cap_rate", "coc", "dscr", "breakeven"}

    def test_red_dscr_score(self):
        v = generate_verdict(_make_result(dscr="0.8"))
        assert v.scores["dscr"] == "red"
