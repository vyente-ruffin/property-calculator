"""Calculate route — T022.

POST /calculate: core endpoint that processes form data and returns
HTMX HTML fragments with investment metrics and verdict.
GET /sidebar/*: swap sidebar partials for property type switching.
"""

from __future__ import annotations

import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".ai" / "logging"))
from logger import get_logger

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from backend.schemas.calculator import CalculatorInput
from backend.services.calculator import calculate
from backend.services.verdict import generate_verdict

router = APIRouter()
templates = Jinja2Templates(directory="templates")
log = get_logger("calculator")


@router.post("/calculate", response_class=HTMLResponse)
async def calculate_property(request: Request):
    """Accept form data, run calculations, return results partial."""
    form = await request.form()
    data = dict(form)

    try:
        inp = CalculatorInput(
            property_type=data.get("property_type", "Commercial"),
            purchase_price=Decimal(str(data.get("purchase_price", "1970000"))),
            down_payment_pct=Decimal(str(data.get("down_payment_pct", "30"))),
            interest_rate=Decimal(str(data.get("interest_rate", "6.5"))),
            loan_years=int(data.get("loan_years", "25")),
            total_units=int(data.get("total_units", "8")),
            state=data.get("state", "CA"),
            property_url=data.get("property_url", ""),
            annual_gross_rents=Decimal(str(data.get("annual_gross_rents", "152195")))
            if data.get("annual_gross_rents")
            else None,
            annual_noi_listing=Decimal(str(data.get("annual_noi_listing", "106548")))
            if data.get("annual_noi_listing")
            else None,
            vacancy_rate=Decimal(str(data.get("vacancy_rate", "3"))) if data.get("vacancy_rate") else None,
            other_expenses=Decimal(str(data.get("other_expenses", "5000"))) if data.get("other_expenses") else None,
            monthly_rent=Decimal(str(data.get("monthly_rent", "5000"))) if data.get("monthly_rent") else None,
        )
    except (InvalidOperation, ValueError) as e:
        log.error("calculation_input_error", error=str(e), form_data=str(data))
        return templates.TemplateResponse(
            request=request,
            name="partials/results_overview.html",
            context={"error": str(e), "params": data},
        )

    result = calculate(inp)
    verdict = generate_verdict(result)

    log.info("calculation_completed",
             property_type=inp.property_type,
             purchase_price=str(inp.purchase_price),
             state=inp.state,
             verdict=verdict.verdict,
             cash_flow=str(result.annual_cash_flow),
             coc=str(result.cash_on_cash))

    # Build URL params for HX-Push-Url
    params = "&".join(f"{k}={v}" for k, v in data.items() if v)

    response = templates.TemplateResponse(
        request=request,
        name="partials/results_overview.html",
        context={"r": result, "v": verdict, "inp": inp, "params": data},
    )
    response.headers["HX-Push-Url"] = f"/?{params}"
    return response


@router.get("/sidebar/commercial", response_class=HTMLResponse)
async def sidebar_commercial(request: Request):
    """Return commercial sidebar partial for HTMX swap."""
    params = dict(request.query_params)
    return templates.TemplateResponse(
        request=request,
        name="partials/sidebar_commercial.html",
        context={"params": params},
    )


@router.get("/sidebar/residential", response_class=HTMLResponse)
async def sidebar_residential(request: Request):
    """Return residential sidebar partial for HTMX swap."""
    params = dict(request.query_params)
    return templates.TemplateResponse(
        request=request,
        name="partials/sidebar_residential.html",
        context={"params": params},
    )
