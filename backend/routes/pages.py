"""Page-fragment routes served as HTML partials (HTMX targets)."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from backend.services.sheets import SheetsNotConfiguredError, SheetsService

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="templates")


@router.get("/compare", response_class=HTMLResponse)
async def compare_deals(request: Request):
    """Return side-by-side comparison of selected portfolio deals."""
    rows_param = request.query_params.get("rows", "")
    if not rows_param:
        return HTMLResponse("<p>No deals selected for comparison</p>", status_code=400)

    try:
        row_indices = [int(r) for r in rows_param.split(",")]
    except ValueError:
        return HTMLResponse("<p>Invalid row numbers</p>", status_code=400)

    try:
        sheets = SheetsService()
        all_props = sheets.get_all_properties()
        properties = [all_props[i - 2] for i in row_indices if 2 <= i <= len(all_props) + 1]
    except SheetsNotConfiguredError:
        properties = []

    return templates.TemplateResponse(
        request=request,
        name="partials/compare_columns.html",
        context={"properties": properties},
    )


@router.get("/tab/portfolio", response_class=HTMLResponse)
async def tab_portfolio(request: Request):
    """Return the portfolio table partial for the calc panel."""
    try:
        svc = SheetsService()
        properties = svc.get_all_properties()
        summary = svc.get_summary()
    except SheetsNotConfiguredError:
        properties = []
        summary = {"total_deals": 0, "good_deals": 0, "bad_deals": 0}
    return templates.TemplateResponse(
        request=request,
        name="partials/portfolio_table.html",
        context={"properties": properties, "summary": summary},
    )
