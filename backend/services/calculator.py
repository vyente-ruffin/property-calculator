"""Calculator service — T008.

Pure functions that implement the property analysis formulas
from app.py, validated against Excel spreadsheets.

All arithmetic uses ``Decimal`` for precision.
Money values are quantized to 2 decimal places.
"""

from __future__ import annotations

from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal

from backend.data.states import get_state_rates
from backend.schemas.calculator import CalculationResult, CalculatorInput, OccupancyScenario

_Q2 = Decimal("0.01")  # quantize target for money
_HUNDRED = Decimal("100")
_TWELVE = Decimal("12")
_PM_COMMERCIAL_PCT = Decimal("0.04")
_PM_RESIDENTIAL_PCT = Decimal("0.10")
_CLOSING_COST_PCT = Decimal("0.03")
_RESIDENTIAL_INSURANCE_RATE = Decimal("0.01")  # flat 1%, NOT state-based
_RESIDENTIAL_MAINTENANCE_MONTHLY = Decimal("250")


def _monthly_payment(loan_amount: Decimal, annual_rate: Decimal, years: int) -> Decimal:
    """Standard amortization formula matching app.py line 201.

    monthly_pi = L * (r * (1+r)^n) / ((1+r)^n - 1)
    Uses float internally for pow() then converts back to Decimal.
    """
    r = float(annual_rate / _HUNDRED) / 12
    n = years * 12
    principal = float(loan_amount)
    if r == 0:
        return Decimal(str(principal / n)).quantize(_Q2, rounding=ROUND_HALF_UP)
    factor = (1 + r) ** n
    payment = principal * (r * factor) / (factor - 1)
    return Decimal(str(payment)).quantize(_Q2, rounding=ROUND_HALF_UP)


# ── Commercial ──────────────────────────────────────────────────


def calculate_commercial(inp: CalculatorInput) -> CalculationResult:
    """Compute all commercial metrics — mirrors app.py lines 499-601."""
    rates = get_state_rates(inp.state)
    insurance_rate: Decimal = rates["insurance_rate"]
    tax_rate: Decimal = rates["tax_rate"]

    purchase = inp.purchase_price
    down_pct = inp.down_payment_pct / _HUNDRED
    gross = inp.annual_gross_rents or Decimal("0")
    vacancy = (inp.vacancy_rate or Decimal("0")) / _HUNDRED
    other_exp = inp.other_expenses or Decimal("0")
    noi_listing_val = inp.annual_noi_listing if inp.annual_noi_listing is not None else Decimal("0")

    # Loan basics
    amount_down = (purchase * down_pct).quantize(_Q2, rounding=ROUND_HALF_UP)
    closing_costs = (purchase * _CLOSING_COST_PCT).quantize(_Q2, rounding=ROUND_HALF_UP)
    total_cash_down = (amount_down + closing_costs).quantize(_Q2, rounding=ROUND_HALF_UP)
    loan_amount = (purchase - amount_down).quantize(_Q2, rounding=ROUND_HALF_UP)

    mp = _monthly_payment(loan_amount, inp.interest_rate, inp.loan_years)
    ads = (mp * _TWELVE).quantize(_Q2, rounding=ROUND_HALF_UP)

    # Operating expenses (app.py lines 502-508)
    annual_insurance = (purchase * insurance_rate).quantize(_Q2, rounding=ROUND_HALF_UP)
    annual_tax = (purchase * tax_rate).quantize(_Q2, rounding=ROUND_HALF_UP)
    annual_pm = (gross * _PM_COMMERCIAL_PCT).quantize(_Q2, rounding=ROUND_HALF_UP)
    total_opex = (annual_insurance + annual_tax + annual_pm + other_exp).quantize(_Q2, rounding=ROUND_HALF_UP)

    # NOI (app.py line 509)
    adjusted_gross = (gross * (Decimal("1") - vacancy)).quantize(_Q2, rounding=ROUND_HALF_UP)
    noi_estimated = (adjusted_gross - total_opex).quantize(_Q2, rounding=ROUND_HALF_UP)

    # Cash flow
    annual_cf = (noi_estimated - ads).quantize(_Q2, rounding=ROUND_HALF_UP)

    # Ratios
    cap_rate = (noi_estimated / purchase * _HUNDRED).quantize(_Q2, rounding=ROUND_HALF_UP) if purchase else Decimal("0")
    cash_on_cash = (
        (annual_cf / total_cash_down * _HUNDRED).quantize(_Q2, rounding=ROUND_HALF_UP)
        if total_cash_down
        else Decimal("0")
    )
    dscr = (noi_estimated / ads).quantize(_Q2, rounding=ROUND_HALF_UP) if ads else Decimal("0")
    ppu = (purchase / inp.total_units).quantize(_Q2, rounding=ROUND_HALF_UP)
    breakeven = (
        ((total_opex + ads) / gross * _HUNDRED).quantize(_Q2, rounding=ROUND_HALF_UP) if gross else Decimal("0")
    )
    grm = (purchase / gross).quantize(_Q2, rounding=ROUND_HALF_UP) if gross else Decimal("0")

    # NOI delta
    noi_delta = (
        ((noi_estimated - noi_listing_val) / noi_listing_val * _HUNDRED).quantize(_Q2, rounding=ROUND_HALF_UP)
        if noi_listing_val
        else Decimal("0")
    )

    return CalculationResult(
        noi_estimated=noi_estimated,
        noi_listing=noi_listing_val,
        noi_delta_pct=noi_delta,
        cap_rate=cap_rate,
        cash_on_cash=cash_on_cash,
        dscr=dscr,
        price_per_unit=ppu,
        breakeven_occ=breakeven,
        grm=grm,
        annual_cash_flow=annual_cf,
        monthly_payment=mp,
        annual_debt_service=ads,
        amount_down=amount_down,
        closing_costs=closing_costs,
        total_cash_down=total_cash_down,
        loan_amount=loan_amount,
        monthly_insurance=(annual_insurance / _TWELVE).quantize(_Q2, rounding=ROUND_HALF_UP),
        monthly_tax=(annual_tax / _TWELVE).quantize(_Q2, rounding=ROUND_HALF_UP),
        monthly_pm=(annual_pm / _TWELVE).quantize(_Q2, rounding=ROUND_HALF_UP),
        monthly_other=(other_exp / _TWELVE).quantize(_Q2, rounding=ROUND_HALF_UP) if other_exp else Decimal("0"),
        annual_insurance=annual_insurance,
        annual_tax=annual_tax,
        annual_pm=annual_pm,
        annual_other=other_exp,
        total_opex=total_opex,
        insurance_rate_pct=(insurance_rate * _HUNDRED).quantize(Decimal("0.1"), rounding=ROUND_HALF_EVEN),
        tax_rate_pct=(tax_rate * _HUNDRED).quantize(Decimal("0.1"), rounding=ROUND_HALF_EVEN),
    )


# ── Residential ─────────────────────────────────────────────────


def calculate_residential(inp: CalculatorInput) -> CalculationResult:
    """Compute all residential metrics — mirrors app.py lines 195-261."""
    rates = get_state_rates(inp.state)
    tax_rate: Decimal = rates["tax_rate"]
    rent = inp.monthly_rent or Decimal("0")
    vacancy = (inp.vacancy_rate or Decimal("0")) / _HUNDRED

    purchase = inp.purchase_price
    down_pct = inp.down_payment_pct / _HUNDRED

    # Loan basics
    amount_down = (purchase * down_pct).quantize(_Q2, rounding=ROUND_HALF_UP)
    closing_costs = (purchase * _CLOSING_COST_PCT).quantize(_Q2, rounding=ROUND_HALF_UP)
    total_cash_down = (amount_down + closing_costs).quantize(_Q2, rounding=ROUND_HALF_UP)
    loan_amount = (purchase - amount_down).quantize(_Q2, rounding=ROUND_HALF_UP)

    mp = _monthly_payment(loan_amount, inp.interest_rate, inp.loan_years)
    ads = (mp * _TWELVE).quantize(_Q2, rounding=ROUND_HALF_UP)

    # Monthly expenses (app.py lines 204-209) — FLAT 1% insurance
    monthly_insurance = (purchase * _RESIDENTIAL_INSURANCE_RATE / _TWELVE).quantize(_Q2, rounding=ROUND_HALF_UP)
    monthly_tax = (purchase * tax_rate / _TWELVE).quantize(_Q2, rounding=ROUND_HALF_UP)
    monthly_pm = (rent * _PM_RESIDENTIAL_PCT).quantize(_Q2, rounding=ROUND_HALF_UP)
    monthly_maint = _RESIDENTIAL_MAINTENANCE_MONTHLY

    # Annual operating expenses (excludes debt service)
    annual_opex = ((monthly_insurance + monthly_tax + monthly_pm + monthly_maint) * _TWELVE).quantize(
        _Q2, rounding=ROUND_HALF_UP
    )

    # Income & NOI
    annual_gross = (rent * _TWELVE).quantize(_Q2, rounding=ROUND_HALF_UP)
    adjusted_gross = (annual_gross * (Decimal("1") - vacancy)).quantize(_Q2, rounding=ROUND_HALF_UP)
    noi_estimated = (adjusted_gross - annual_opex).quantize(_Q2, rounding=ROUND_HALF_UP)

    # Cash flow
    annual_cf = (noi_estimated - ads).quantize(_Q2, rounding=ROUND_HALF_UP)

    # Ratios
    cap_rate = (noi_estimated / purchase * _HUNDRED).quantize(_Q2, rounding=ROUND_HALF_UP) if purchase else Decimal("0")
    cash_on_cash = (
        (annual_cf / total_cash_down * _HUNDRED).quantize(_Q2, rounding=ROUND_HALF_UP)
        if total_cash_down
        else Decimal("0")
    )
    dscr = (noi_estimated / ads).quantize(_Q2, rounding=ROUND_HALF_UP) if ads else Decimal("0")
    ppu = (purchase / inp.total_units).quantize(_Q2, rounding=ROUND_HALF_UP)
    breakeven = (
        ((annual_opex + ads) / annual_gross * _HUNDRED).quantize(_Q2, rounding=ROUND_HALF_UP)
        if annual_gross
        else Decimal("0")
    )
    grm = (purchase / annual_gross).quantize(_Q2, rounding=ROUND_HALF_UP) if annual_gross else Decimal("0")

    # Occupancy scenarios (75%, 90%, 100%)
    monthly_expenses = (mp + monthly_insurance + monthly_tax + monthly_pm + monthly_maint).quantize(
        _Q2, rounding=ROUND_HALF_UP
    )
    scenarios: list[OccupancyScenario] = []
    for occ in (75, 90, 100):
        occ_rate = Decimal(str(occ)) / _HUNDRED
        occ_monthly_income = (rent * occ_rate).quantize(_Q2, rounding=ROUND_HALF_UP)
        occ_monthly_cf = (occ_monthly_income - monthly_expenses).quantize(_Q2, rounding=ROUND_HALF_UP)
        occ_annual_cf = (occ_monthly_cf * _TWELVE).quantize(_Q2, rounding=ROUND_HALF_UP)
        occ_roi = (
            (occ_annual_cf / total_cash_down * _HUNDRED).quantize(_Q2, rounding=ROUND_HALF_UP)
            if total_cash_down
            else Decimal("0")
        )
        scenarios.append(OccupancyScenario(occupancy_pct=occ, monthly_cash_flow=occ_monthly_cf, annual_roi=occ_roi))

    # Investment status based on 75% occupancy cash flow
    worst_cf = scenarios[0].monthly_cash_flow
    inv_status = "Good Investment" if worst_cf >= 0 else "High Risk"

    # Annual expense breakdowns for residential
    annual_insurance_val = (monthly_insurance * _TWELVE).quantize(_Q2, rounding=ROUND_HALF_UP)
    annual_tax_val = (monthly_tax * _TWELVE).quantize(_Q2, rounding=ROUND_HALF_UP)
    annual_pm_val = (monthly_pm * _TWELVE).quantize(_Q2, rounding=ROUND_HALF_UP)

    return CalculationResult(
        noi_estimated=noi_estimated,
        noi_listing=Decimal("0"),
        noi_delta_pct=Decimal("0"),
        cap_rate=cap_rate,
        cash_on_cash=cash_on_cash,
        dscr=dscr,
        price_per_unit=ppu,
        breakeven_occ=breakeven,
        grm=grm,
        annual_cash_flow=annual_cf,
        monthly_payment=mp,
        annual_debt_service=ads,
        amount_down=amount_down,
        closing_costs=closing_costs,
        total_cash_down=total_cash_down,
        loan_amount=loan_amount,
        occupancy_scenarios=scenarios,
        investment_status=inv_status,
        monthly_insurance=monthly_insurance,
        monthly_tax=monthly_tax,
        monthly_pm=monthly_pm,
        monthly_maintenance=monthly_maint,
        annual_insurance=annual_insurance_val,
        annual_tax=annual_tax_val,
        annual_pm=annual_pm_val,
        total_opex=annual_opex,
        insurance_rate_pct=(_RESIDENTIAL_INSURANCE_RATE * _HUNDRED).quantize(Decimal("0.1"), rounding=ROUND_HALF_EVEN),
        tax_rate_pct=(tax_rate * _HUNDRED).quantize(Decimal("0.1"), rounding=ROUND_HALF_EVEN),
    )


# ── Dispatcher ──────────────────────────────────────────────────


def calculate(inp: CalculatorInput) -> CalculationResult:
    """Route to the correct calculator based on property_type."""
    ptype = inp.property_type.strip().title()
    if ptype == "Commercial":
        return calculate_commercial(inp)
    if ptype == "Residential":
        return calculate_residential(inp)
    raise ValueError(f"Unknown property type: {inp.property_type!r}")
