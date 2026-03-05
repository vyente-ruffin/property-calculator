"""Portfolio routes — save and view parsed properties."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from backend.services.portfolio import get_all_properties, save_property

router = APIRouter()
templates = Jinja2Templates(directory="templates")


class PortfolioSaveRequest(BaseModel):
    data: dict


@router.post("/api/portfolio")
async def save_to_portfolio(req: PortfolioSaveRequest):
    pid = save_property(req.data)
    return JSONResponse({"id": pid, "status": "saved"})


@router.get("/tab/portfolio", response_class=HTMLResponse)
async def portfolio_view(request: Request):
    properties = get_all_properties()
    return templates.TemplateResponse(
        request=request,
        name="partials/portfolio.html",
        context={"properties": properties},
    )
