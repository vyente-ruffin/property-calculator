import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".ai" / "logging"))
from logger import setup_logging, get_logger

setup_logging(project="property-calculator")
log = get_logger("server")

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.routes.calculator import router as calc_router
from backend.routes.health import router as health_router
from backend.routes.pages import router as pages_router
from backend.routes.parse import router as parse_router
from backend.routes.sheets import router as sheets_router
from backend.routes.portfolio import router as portfolio_router

app = FastAPI(title="Property Parser")

templates = Jinja2Templates(directory="templates")

# API routes
app.include_router(health_router, prefix="/api")
app.include_router(parse_router, prefix="/api")
app.include_router(sheets_router, prefix="/api")
app.include_router(calc_router)
app.include_router(pages_router)
app.include_router(portfolio_router)

# Serve favicon
@app.get("/favicon.png")
async def favicon():
    return FileResponse("favicon.png")

# Serve legacy frontend static files
app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
app.mount("/js", StaticFiles(directory="frontend/js"), name="js")

# New static file mount
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index(request: Request):
    params = dict(request.query_params)
    context: dict = {"params": params}

    # Pre-render results when query params contain calculator inputs
    if params.get("purchase_price"):
        from decimal import Decimal

        from backend.schemas.calculator import CalculatorInput
        from backend.services.calculator import calculate
        from backend.services.verdict import generate_verdict

        try:
            inp = CalculatorInput(
                property_type=params.get("property_type", "Commercial"),
                purchase_price=Decimal(params.get("purchase_price", "1970000")),
                down_payment_pct=Decimal(params.get("down_payment_pct", "30")),
                interest_rate=Decimal(params.get("interest_rate", "6.5")),
                loan_years=int(params.get("loan_years", "25")),
                total_units=int(params.get("total_units", "8")),
                state=params.get("state", "CA"),
                property_url=params.get("property_url", ""),
                annual_gross_rents=Decimal(params["annual_gross_rents"]) if params.get("annual_gross_rents") else None,
                annual_noi_listing=Decimal(params["annual_noi_listing"]) if params.get("annual_noi_listing") else None,
                vacancy_rate=Decimal(params["vacancy_rate"]) if params.get("vacancy_rate") else None,
                other_expenses=Decimal(params["other_expenses"]) if params.get("other_expenses") else None,
                monthly_rent=Decimal(params["monthly_rent"]) if params.get("monthly_rent") else None,
            )
            result = calculate(inp)
            verdict = generate_verdict(result)
            context["r"] = result
            context["v"] = verdict
            context["inp"] = inp
            log.info("calculation_rendered",
                      property_type=inp.property_type,
                      purchase_price=str(inp.purchase_price),
                      state=inp.state,
                      verdict=verdict.verdict)
        except Exception as e:
            log.error("calculation_failed", error=str(e))

    return templates.TemplateResponse(request, "index.html", context=context)


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8090, reload=True)
