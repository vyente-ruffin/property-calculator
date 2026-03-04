"""Verdict Engine — T009.

Evaluates a ``CalculationResult`` against investment thresholds
and produces an overall verdict (INVEST / REVIEW / PASS) with
scored metrics and descriptive reasons.
"""

from __future__ import annotations

from decimal import Decimal

from backend.data.thresholds import THRESHOLDS, score_metric
from backend.schemas.calculator import CalculationResult

_METRIC_LABELS = {
    "cap_rate": "Cap Rate",
    "coc": "Cash-on-Cash",
    "dscr": "DSCR",
    "breakeven": "Break-Even Occupancy",
}

_METRIC_FORMATS: dict[str, str] = {
    "cap_rate": "{value}%",
    "coc": "{value}%",
    "dscr": "{value}x",
    "breakeven": "{value}%",
}

_SCORE_ADJECTIVE = {
    "green": "strong",
    "yellow": "moderate",
    "red": "weak",
}


class Verdict:
    """Container for verdict result."""

    def __init__(self, verdict: str, reasons: list[str], scores: dict[str, str]):
        self.verdict = verdict
        self.reasons = reasons
        self.scores = scores


def _format_value(metric: str, value: Decimal) -> str:
    return _METRIC_FORMATS[metric].format(value=value)


def _build_reason(metric: str, value: Decimal, score: str) -> str:
    label = _METRIC_LABELS[metric]
    formatted = _format_value(metric, value)
    threshold_info = THRESHOLDS[metric][score]
    adj = _SCORE_ADJECTIVE[score]
    return f"{label} {formatted} is {adj} ({threshold_info})"


def generate_verdict(result: CalculationResult) -> Verdict:
    """Score all metrics and produce an investment verdict.

    Returns a ``Verdict`` with exactly 3 descriptive reasons.
    """
    values: dict[str, Decimal] = {
        "cap_rate": result.cap_rate,
        "coc": result.cash_on_cash,
        "dscr": result.dscr,
        "breakeven": result.breakeven_occ,
    }

    scores = {m: score_metric(m, v) for m, v in values.items()}

    has_red = any(s == "red" for s in scores.values())
    all_green = all(s == "green" for s in scores.values())
    dscr_below_one = values["dscr"] < Decimal("1.0")

    if has_red or dscr_below_one:
        verdict = "PASS"
    elif all_green:
        verdict = "INVEST"
    else:
        verdict = "REVIEW"

    # Build reasons, prioritising red → yellow → green
    priority = {"red": 0, "yellow": 1, "green": 2}
    ranked = sorted(values.keys(), key=lambda m: (priority[scores[m]], m))

    reasons: list[str] = []
    for metric in ranked:
        reasons.append(_build_reason(metric, values[metric], scores[metric]))

    # Always return exactly 3 reasons
    while len(reasons) < 3:
        reasons.append(reasons[-1])
    reasons = reasons[:3]

    return Verdict(verdict=verdict, reasons=reasons, scores=scores)
