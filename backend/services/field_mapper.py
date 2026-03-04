"""Field mapper — T023.

Maps parsed PropertyData display-dict → CalculatorInput.
Handles currency stripping, state extraction, property type detection.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from backend.schemas.calculator import CalculatorInput

_DEFAULTS = CalculatorInput()

# Matches "City, ST" or "City, ST ZIP" or "City, ST ZIP-EXT"
_STATE_RE = re.compile(r",\s*([A-Z]{2})\b")


def _parse_currency(value: str | None) -> Decimal | None:
    """Strip '$' and ',' from a currency string and return Decimal, or None."""
    if value is None:
        return None
    cleaned = value.replace("$", "").replace(",", "").strip()
    if not cleaned:
        return None
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def _extract_state(city_field: str | None) -> str | None:
    """Extract 2-letter state abbreviation from 'City, ST ZIP' format."""
    if city_field is None:
        return None
    match = _STATE_RE.search(city_field)
    return match.group(1) if match else None


def map_property_to_input(data: dict) -> CalculatorInput:
    """Convert a parsed property display-dict into a validated CalculatorInput.

    Uses display-key names (e.g. "Price", "Annual Rent Income (Projected)")
    matching PropertyData.to_display_dict() output.
    """
    fields: dict = {}

    # Currency fields
    price = _parse_currency(data.get("Price"))
    if price is not None:
        fields["purchase_price"] = price

    noi = _parse_currency(data.get("NOI"))
    if noi is not None:
        fields["annual_noi_listing"] = noi

    gross_rents = _parse_currency(data.get("Annual Rent Income (Projected)"))
    if gross_rents is not None:
        fields["annual_gross_rents"] = gross_rents

    monthly_rent = _parse_currency(
        data.get("Monthly Rental Income (Projected)")
    )
    if monthly_rent is not None:
        fields["monthly_rent"] = monthly_rent

    # State from City field
    state = _extract_state(data.get("City"))
    if state is not None:
        fields["state"] = state

    # Total Units
    units = data.get("Total Units")
    if units is not None:
        fields["total_units"] = int(units)

    # Property URL
    link = data.get("Link")
    if link is not None:
        fields["property_url"] = link
    else:
        fields["property_url"] = ""

    # Property type detection: > 4 units → Commercial, else Residential
    resolved_units = fields.get("total_units")
    if resolved_units is not None and resolved_units > 4:
        fields["property_type"] = "Commercial"
    else:
        fields["property_type"] = "Residential"

    return CalculatorInput(**fields)
