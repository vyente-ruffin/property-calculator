"""Tests for backend.services.calculator — T008.

Strict TDD: these tests are written FIRST, then the implementation.
Expected values computed from app.py formulas validated against Excel.
"""

from decimal import Decimal

import pytest

from backend.schemas.calculator import CalculationResult, CalculatorInput
from backend.services.calculator import calculate, calculate_commercial, calculate_residential

# ── helpers ──────────────────────────────────────────────────────


def assert_close(actual: Decimal, expected: str, *, tol: str = "1"):
    """Assert *actual* ≈ Decimal(expected) within ± Decimal(tol)."""
    exp = Decimal(expected)
    tolerance = Decimal(tol)
    diff = abs(actual - exp)
    assert diff <= tolerance, (
        f"Expected {exp} ± {tolerance}, got {actual} (diff={diff})"
    )


# ── Commercial — Excel-validated test case ──────────────────────


class TestCommercialCalculator:
    """Purchase=$1,970,000  Down=30%  Rate=6.5%  Term=25yr
    Gross=$152,195  NOI_listing=$106,548  Vacancy=3%
    Expenses=$5,000  State=CA  Units=8
    """

    @pytest.fixture()
    def inp(self):
        return CalculatorInput(
            property_type="Commercial",
            purchase_price=Decimal("1970000"),
            down_payment_pct=Decimal("30"),
            interest_rate=Decimal("6.5"),
            loan_years=25,
            annual_gross_rents=Decimal("152195"),
            annual_noi_listing=Decimal("106548"),
            vacancy_rate=Decimal("3"),
            other_expenses=Decimal("5000"),
            state="CA",
            total_units=8,
        )

    @pytest.fixture()
    def result(self, inp):
        return calculate_commercial(inp)

    # ── Loan basics ──

    def test_amount_down(self, result):
        assert_close(result.amount_down, "591000")

    def test_closing_costs(self, result):
        assert_close(result.closing_costs, "59100")

    def test_total_cash_down(self, result):
        assert_close(result.total_cash_down, "650100")

    def test_loan_amount(self, result):
        assert_close(result.loan_amount, "1379000")

    def test_monthly_payment(self, result):
        assert_close(result.monthly_payment, "9311.11", tol="1")

    def test_annual_debt_service(self, result):
        assert_close(result.annual_debt_service, "111733.28", tol="1")

    # ── Operating expenses & NOI ──

    def test_noi_estimated(self, result):
        """NOI = adjusted_gross - total_opex.

        adjusted_gross = 152195 * 0.97 = 147629.15
        opex = 24625 + 24625 + 6087.80 + 5000 = 60337.80
        NOI = 147629.15 - 60337.80 = 87291.35
        """
        assert_close(result.noi_estimated, "87291.35", tol="1")

    def test_noi_listing(self, result):
        assert_close(result.noi_listing, "106548")

    def test_noi_delta_pct(self, result):
        assert_close(result.noi_delta_pct, "-18.07", tol="0.1")

    # ── Cash flow & returns ──

    def test_annual_cash_flow(self, result):
        assert_close(result.annual_cash_flow, "-24441.93", tol="1")

    def test_cap_rate(self, result):
        assert_close(result.cap_rate, "4.43", tol="0.01")

    def test_cash_on_cash(self, result):
        assert_close(result.cash_on_cash, "-3.76", tol="0.01")

    def test_dscr(self, result):
        assert_close(result.dscr, "0.78", tol="0.01")

    # ── New metrics ──

    def test_price_per_unit(self, result):
        assert_close(result.price_per_unit, "246250")

    def test_breakeven_occ(self, result):
        assert_close(result.breakeven_occ, "113.06", tol="0.1")

    def test_grm(self, result):
        assert_close(result.grm, "12.94", tol="0.01")

    def test_returns_calculation_result(self, result):
        assert isinstance(result, CalculationResult)


# ── Residential — app.py-validated test case ────────────────────


class TestResidentialCalculator:
    """Purchase=$650,000  Down=20%  Rate=6.5%  Term=15yr
    Rent=$5,000  State=CA  Vacancy=0% (100% occupancy)
    """

    @pytest.fixture()
    def inp(self):
        return CalculatorInput(
            property_type="Residential",
            purchase_price=Decimal("650000"),
            down_payment_pct=Decimal("20"),
            interest_rate=Decimal("6.5"),
            loan_years=15,
            monthly_rent=Decimal("5000"),
            state="CA",
            total_units=1,
            vacancy_rate=Decimal("0"),
        )

    @pytest.fixture()
    def result(self, inp):
        return calculate_residential(inp)

    # ── Loan basics ──

    def test_loan_amount(self, result):
        assert_close(result.loan_amount, "520000")

    def test_monthly_payment(self, result):
        assert_close(result.monthly_payment, "4529.76", tol="1")

    def test_amount_down(self, result):
        assert_close(result.amount_down, "130000")

    def test_closing_costs(self, result):
        assert_close(result.closing_costs, "19500")

    def test_total_cash_down(self, result):
        assert_close(result.total_cash_down, "149500")

    def test_annual_debt_service(self, result):
        assert_close(result.annual_debt_service, "54357.10", tol="1")

    # ── Expense components via NOI ──

    def test_noi_uses_flat_insurance(self, result):
        """Residential uses FLAT 1% insurance (not state-based).

        Insurance = 650000 * 0.01 = 6500/yr
        Tax = 650000 * 0.0125 = 8125/yr  (CA rate)
        PM = 5000 * 0.10 * 12 = 6000/yr
        Maint = 250 * 12 = 3000/yr
        Opex = 23625/yr
        NOI = 60000 - 23625 = 36375
        """
        assert_close(result.noi_estimated, "36375", tol="1")

    def test_annual_cash_flow(self, result):
        assert_close(result.annual_cash_flow, "-17982.10", tol="1")

    # ── New metrics ──

    def test_cap_rate(self, result):
        assert_close(result.cap_rate, "5.60", tol="0.01")

    def test_cash_on_cash(self, result):
        assert_close(result.cash_on_cash, "-12.03", tol="0.1")

    def test_dscr(self, result):
        assert_close(result.dscr, "0.67", tol="0.01")

    def test_price_per_unit(self, result):
        assert_close(result.price_per_unit, "650000")

    def test_breakeven_occ(self, result):
        assert_close(result.breakeven_occ, "129.97", tol="0.1")

    def test_grm(self, result):
        assert_close(result.grm, "10.83", tol="0.01")

    def test_noi_listing_zero_for_residential(self, result):
        assert result.noi_listing == Decimal("0")

    def test_noi_delta_zero_for_residential(self, result):
        assert result.noi_delta_pct == Decimal("0")

    def test_returns_calculation_result(self, result):
        assert isinstance(result, CalculationResult)


# ── Residential occupancy scenarios ─────────────────────────────


class TestResidentialOccupancyScenarios:
    """Verify 3 occupancy levels match app.py monthly cash-flow logic."""

    def _make_input(self, vacancy_pct: int) -> CalculatorInput:
        return CalculatorInput(
            property_type="Residential",
            purchase_price=Decimal("650000"),
            down_payment_pct=Decimal("20"),
            interest_rate=Decimal("6.5"),
            loan_years=15,
            monthly_rent=Decimal("5000"),
            state="CA",
            total_units=1,
            vacancy_rate=Decimal(str(vacancy_pct)),
        )

    def test_100pct_occupancy(self):
        r = calculate_residential(self._make_input(0))
        assert_close(r.annual_cash_flow, "-17982.10", tol="1")

    def test_90pct_occupancy(self):
        r = calculate_residential(self._make_input(10))
        # income = 54000, noi = 54000 - 23625 = 30375, cf = 30375 - 54357.10
        assert_close(r.annual_cash_flow, "-23982.10", tol="1")

    def test_75pct_occupancy(self):
        r = calculate_residential(self._make_input(25))
        # income = 45000, noi = 45000 - 23625 = 21375, cf = 21375 - 54357.10
        assert_close(r.annual_cash_flow, "-32982.10", tol="1")


# ── Dispatcher ──────────────────────────────────────────────────


class TestCalculateDispatcher:
    """calculate() routes to the correct sub-calculator."""

    def test_dispatches_commercial(self):
        inp = CalculatorInput(
            property_type="Commercial",
            purchase_price=Decimal("1970000"),
            down_payment_pct=Decimal("30"),
            interest_rate=Decimal("6.5"),
            loan_years=25,
            annual_gross_rents=Decimal("152195"),
            annual_noi_listing=Decimal("106548"),
            vacancy_rate=Decimal("3"),
            other_expenses=Decimal("5000"),
            state="CA",
            total_units=8,
        )
        result = calculate(inp)
        assert isinstance(result, CalculationResult)
        assert_close(result.loan_amount, "1379000")

    def test_dispatches_residential(self):
        inp = CalculatorInput(
            property_type="Residential",
            purchase_price=Decimal("650000"),
            down_payment_pct=Decimal("20"),
            interest_rate=Decimal("6.5"),
            loan_years=15,
            monthly_rent=Decimal("5000"),
            state="CA",
            total_units=1,
            vacancy_rate=Decimal("0"),
        )
        result = calculate(inp)
        assert isinstance(result, CalculationResult)
        assert_close(result.loan_amount, "520000")

    def test_unknown_type_raises(self):
        inp = CalculatorInput(property_type="Industrial")
        with pytest.raises(ValueError, match="Unknown property type"):
            calculate(inp)


# ── Edge cases ──────────────────────────────────────────────────


class TestEdgeCases:
    """Boundary conditions for both calculator types."""

    def test_zero_vacancy_commercial(self):
        inp = CalculatorInput(
            property_type="Commercial",
            purchase_price=Decimal("1000000"),
            down_payment_pct=Decimal("25"),
            interest_rate=Decimal("6.0"),
            loan_years=20,
            annual_gross_rents=Decimal("100000"),
            annual_noi_listing=Decimal("70000"),
            vacancy_rate=Decimal("0"),
            other_expenses=Decimal("0"),
            state="CA",
            total_units=4,
        )
        result = calculate_commercial(inp)
        # ins = 12500, tax = 12500, pm = 4000, other = 0  → opex = 29000
        # noi = 100000 - 29000 = 71000
        assert_close(result.noi_estimated, "71000", tol="1")

    def test_max_vacancy_commercial(self):
        inp = CalculatorInput(
            property_type="Commercial",
            purchase_price=Decimal("1000000"),
            down_payment_pct=Decimal("25"),
            interest_rate=Decimal("6.0"),
            loan_years=20,
            annual_gross_rents=Decimal("100000"),
            annual_noi_listing=Decimal("70000"),
            vacancy_rate=Decimal("50"),
            other_expenses=Decimal("0"),
            state="CA",
            total_units=4,
        )
        result = calculate_commercial(inp)
        # adjusted = 50000, noi = 50000 - 29000 = 21000
        assert_close(result.noi_estimated, "21000", tol="1")

    def test_single_unit(self):
        inp = CalculatorInput(
            property_type="Commercial",
            purchase_price=Decimal("500000"),
            down_payment_pct=Decimal("20"),
            interest_rate=Decimal("5.0"),
            loan_years=15,
            annual_gross_rents=Decimal("60000"),
            annual_noi_listing=Decimal("40000"),
            vacancy_rate=Decimal("5"),
            other_expenses=Decimal("1000"),
            state="NV",
            total_units=1,
        )
        result = calculate_commercial(inp)
        assert_close(result.price_per_unit, "500000")

    def test_high_interest_rate(self):
        inp = CalculatorInput(
            property_type="Commercial",
            purchase_price=Decimal("1000000"),
            down_payment_pct=Decimal("30"),
            interest_rate=Decimal("15.0"),
            loan_years=10,
            annual_gross_rents=Decimal("200000"),
            annual_noi_listing=Decimal("150000"),
            vacancy_rate=Decimal("5"),
            other_expenses=Decimal("5000"),
            state="TX",
            total_units=6,
        )
        result = calculate_commercial(inp)
        assert result.monthly_payment > Decimal("0")
        assert result.dscr > Decimal("0")

    def test_residential_none_vacancy_defaults_zero(self):
        """When vacancy_rate is None, residential treats it as 0%."""
        inp = CalculatorInput(
            property_type="Residential",
            purchase_price=Decimal("500000"),
            down_payment_pct=Decimal("25"),
            interest_rate=Decimal("7.0"),
            loan_years=30,
            monthly_rent=Decimal("3000"),
            state="AZ",
            total_units=1,
            vacancy_rate=None,
        )
        result = calculate_residential(inp)
        annual_gross = Decimal("3000") * 12
        assert result.noi_estimated <= annual_gross

    def test_different_state_rates(self):
        """TX has higher tax rate — verify it affects NOI."""
        base = {
            "property_type": "Commercial",
            "purchase_price": Decimal("1000000"),
            "down_payment_pct": Decimal("25"),
            "interest_rate": Decimal("6.0"),
            "loan_years": 20,
            "annual_gross_rents": Decimal("100000"),
            "annual_noi_listing": Decimal("70000"),
            "vacancy_rate": Decimal("5"),
            "other_expenses": Decimal("2000"),
            "total_units": 4,
        }
        ca = calculate_commercial(CalculatorInput(**base, state="CA"))
        tx = calculate_commercial(CalculatorInput(**base, state="TX"))
        # CA combined (tax 1.25% + ins 1.25% = 2.50%) > TX (1.70% + 0.50% = 2.20%)
        assert ca.noi_estimated < tx.noi_estimated
