"""Metric scoring thresholds — T007.

Scores a metric value as ``"green"``, ``"yellow"``, or ``"red"``
based on predefined investment-quality thresholds.
"""

from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal

# Each entry maps metric name → scoring function
_ScorerFn = Callable[[Decimal], str]


def _score_higher_is_better(green_ge: Decimal, yellow_ge: Decimal) -> _ScorerFn:
    """Factory for metrics where higher values are better."""
    def _score(value: Decimal) -> str:
        if value >= green_ge:
            return "green"
        if value >= yellow_ge:
            return "yellow"
        return "red"
    return _score


def _score_lower_is_better(green_lt: Decimal, red_gt: Decimal) -> _ScorerFn:
    """Factory for metrics where lower values are better."""
    def _score(value: Decimal) -> str:
        if value < green_lt:
            return "green"
        if value <= red_gt:
            return "yellow"
        return "red"
    return _score


THRESHOLDS: dict[str, dict] = {
    "cap_rate": {
        "green": "≥6%",
        "yellow": "4–6%",
        "red": "<4%",
    },
    "coc": {
        "green": "≥8%",
        "yellow": "4–8%",
        "red": "<4%",
    },
    "dscr": {
        "green": "≥1.25",
        "yellow": "1.0–1.25",
        "red": "<1.0",
    },
    "breakeven": {
        "green": "<75%",
        "yellow": "75–85%",
        "red": ">85%",
    },
}

_SCORERS: dict[str, _ScorerFn] = {
    "cap_rate": _score_higher_is_better(Decimal("6"), Decimal("4")),
    "coc": _score_higher_is_better(Decimal("8"), Decimal("4")),
    "dscr": _score_higher_is_better(Decimal("1.25"), Decimal("1.0")),
    "breakeven": _score_lower_is_better(Decimal("75"), Decimal("85")),
}


def score_metric(name: str, value: Decimal) -> str:
    """Return ``"green"``, ``"yellow"``, or ``"red"`` for the given metric.

    Raises ``ValueError`` for unknown metric names.
    """
    scorer = _SCORERS.get(name)
    if scorer is None:
        raise ValueError(f"Unknown metric: {name!r}")
    return scorer(value)
