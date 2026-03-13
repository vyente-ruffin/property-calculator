"""Tests for backend.data.thresholds — T007."""

from decimal import Decimal

import pytest

from backend.data.thresholds import THRESHOLDS, score_metric


class TestCapRate:
    """Cap Rate: ≥6% green, 4-6% yellow, <4% red."""

    def test_green_deep(self):
        assert score_metric("cap_rate", Decimal("10.0")) == "green"

    def test_green_boundary(self):
        assert score_metric("cap_rate", Decimal("6.0")) == "green"

    def test_yellow_just_below(self):
        assert score_metric("cap_rate", Decimal("5.99")) == "yellow"

    def test_yellow_boundary_lower(self):
        assert score_metric("cap_rate", Decimal("4.0")) == "yellow"

    def test_yellow_mid(self):
        assert score_metric("cap_rate", Decimal("5.0")) == "yellow"

    def test_red_just_below(self):
        assert score_metric("cap_rate", Decimal("3.99")) == "red"

    def test_red_deep(self):
        assert score_metric("cap_rate", Decimal("1.0")) == "red"


class TestCashOnCash:
    """Cash-on-Cash: ≥8% green, 4-8% yellow, <4% red."""

    def test_green_deep(self):
        assert score_metric("coc", Decimal("15.0")) == "green"

    def test_green_boundary(self):
        assert score_metric("coc", Decimal("8.0")) == "green"

    def test_yellow_just_below(self):
        assert score_metric("coc", Decimal("7.99")) == "yellow"

    def test_yellow_boundary_lower(self):
        assert score_metric("coc", Decimal("4.0")) == "yellow"

    def test_yellow_mid(self):
        assert score_metric("coc", Decimal("6.0")) == "yellow"

    def test_red_just_below(self):
        assert score_metric("coc", Decimal("3.99")) == "red"

    def test_red_deep(self):
        assert score_metric("coc", Decimal("0.5")) == "red"


class TestDSCR:
    """DSCR: ≥1.25 green, 1.0-1.25 yellow, <1.0 red."""

    def test_green_deep(self):
        assert score_metric("dscr", Decimal("2.0")) == "green"

    def test_green_boundary(self):
        assert score_metric("dscr", Decimal("1.25")) == "green"

    def test_yellow_just_below(self):
        assert score_metric("dscr", Decimal("1.24")) == "yellow"

    def test_yellow_boundary_lower(self):
        assert score_metric("dscr", Decimal("1.0")) == "yellow"

    def test_yellow_mid(self):
        assert score_metric("dscr", Decimal("1.10")) == "yellow"

    def test_red_just_below(self):
        assert score_metric("dscr", Decimal("0.99")) == "red"

    def test_red_deep(self):
        assert score_metric("dscr", Decimal("0.5")) == "red"


class TestBreakevenOccupancy:
    """Break-Even Occupancy: <75% green, 75-85% yellow, >85% red."""

    def test_green_deep(self):
        assert score_metric("breakeven", Decimal("50.0")) == "green"

    def test_green_just_below(self):
        assert score_metric("breakeven", Decimal("74.99")) == "green"

    def test_yellow_boundary_lower(self):
        assert score_metric("breakeven", Decimal("75.0")) == "yellow"

    def test_yellow_mid(self):
        assert score_metric("breakeven", Decimal("80.0")) == "yellow"

    def test_yellow_boundary_upper(self):
        assert score_metric("breakeven", Decimal("85.0")) == "yellow"

    def test_red_just_above(self):
        assert score_metric("breakeven", Decimal("85.01")) == "red"

    def test_red_deep(self):
        assert score_metric("breakeven", Decimal("95.0")) == "red"


class TestThresholdsDict:
    """Verify THRESHOLDS dict has entries for all four metrics."""

    def test_all_metrics_present(self):
        assert set(THRESHOLDS.keys()) == {"cap_rate", "coc", "dscr", "breakeven"}


class TestScoreMetricErrors:
    """score_metric should raise ValueError for unknown metric names."""

    def test_unknown_metric(self):
        with pytest.raises(ValueError, match="Unknown metric"):
            score_metric("nonexistent", Decimal("5.0"))
