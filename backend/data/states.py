"""State-level tax and insurance rates — T006.

Each rate is stored as a Decimal fraction (e.g. 0.62 % → 0.0062).
"""

from __future__ import annotations

from decimal import Decimal

STATE_DATA: dict[str, dict] = {
    "AZ": {"tax_rate": Decimal("0.0062"), "insurance_rate": Decimal("0.0050")},
    "CA": {"tax_rate": Decimal("0.0125"), "insurance_rate": Decimal("0.0125")},
    "IN": {"tax_rate": Decimal("0.0137"), "insurance_rate": Decimal("0.0050")},
    "NV": {"tax_rate": Decimal("0.0065"), "insurance_rate": Decimal("0.0050")},
    "TX": {"tax_rate": Decimal("0.0170"), "insurance_rate": Decimal("0.0050")},
    "MI": {"tax_rate": Decimal("0.0321"), "insurance_rate": Decimal("0.0050")},
}


def get_state_rates(abbrev: str) -> dict:
    """Return tax & insurance rates for *abbrev* (case-insensitive).

    Raises ``ValueError`` for unknown state abbreviations.
    """
    key = abbrev.upper()
    if key not in STATE_DATA:
        raise ValueError(f"Unknown state: {abbrev!r}")
    return STATE_DATA[key]
