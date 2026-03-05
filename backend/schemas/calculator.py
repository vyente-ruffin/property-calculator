"""Calculator Pydantic models — T010.

CalculatorInput  – validated user inputs for the property calculator.
CalculationResult – output model containing all computed metrics.
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class CalculatorInput(BaseModel):
    """Validated inputs for a property calculation."""

    property_type: str = "Commercial"
    purchase_price: Decimal = Decimal("1970000")
    down_payment_pct: Decimal = Field(default=Decimal("30"), ge=0, le=100)
    interest_rate: Decimal = Field(default=Decimal("6.5"), ge=0, le=20)
    loan_years: int = Field(default=25, ge=1, le=30)
    total_units: int = Field(default=8, ge=1)
    state: str = "CA"
    property_url: str = ""

    # Commercial-specific
    annual_gross_rents: Decimal | None = Decimal("152195")
    annual_noi_listing: Decimal | None = Decimal("106548")
    vacancy_rate: Decimal | None = Field(default=Decimal("3"), ge=0, le=50)
    other_expenses: Decimal | None = Decimal("5000")

    # Residential-specific
    monthly_rent: Decimal | None = Decimal("5000")


class OccupancyScenario(BaseModel):
    """Single occupancy scenario for residential analysis."""

    occupancy_pct: int
    monthly_cash_flow: Decimal
    annual_roi: Decimal


class CalculationResult(BaseModel):
    """All computed metrics from a property analysis."""

    noi_estimated: Decimal
    noi_listing: Decimal
    noi_delta_pct: Decimal
    cap_rate: Decimal
    cash_on_cash: Decimal
    dscr: Decimal
    price_per_unit: Decimal
    breakeven_occ: Decimal
    grm: Decimal
    annual_cash_flow: Decimal
    monthly_payment: Decimal
    annual_debt_service: Decimal
    amount_down: Decimal
    closing_costs: Decimal
    total_cash_down: Decimal
    loan_amount: Decimal

    # Expense breakdowns (populated for both property types)
    monthly_insurance: Decimal | None = None
    monthly_tax: Decimal | None = None
    monthly_pm: Decimal | None = None
    monthly_maintenance: Decimal | None = None
    monthly_other: Decimal | None = None
    annual_insurance: Decimal | None = None
    annual_tax: Decimal | None = None
    annual_pm: Decimal | None = None
    annual_other: Decimal | None = None
    total_opex: Decimal | None = None  # operating expenses excl. debt service

    # Display rates (for template rendering)
    insurance_rate_pct: Decimal | None = None
    tax_rate_pct: Decimal | None = None

    # Residential-specific
    occupancy_scenarios: list[OccupancyScenario] | None = None
    investment_status: str | None = None
