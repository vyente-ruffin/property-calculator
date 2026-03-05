"""Portfolio routes — save and view parsed properties."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".ai" / "logging"))
from logger import get_logger

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from backend.services.portfolio import get_all_properties, save_property

router = APIRouter()
templates = Jinja2Templates(directory="templates")
log = get_logger("frontend")


class PortfolioSaveRequest(BaseModel):
    data: dict


class LogEvent(BaseModel):
    event: str
    data: dict = {}


@router.post("/api/portfolio")
async def save_to_portfolio(req: PortfolioSaveRequest):
    pid = save_property(req.data)
    return JSONResponse({"id": pid, "status": "saved"})


@router.post("/api/log")
async def log_frontend_event(req: LogEvent):
    log.info(req.event, **req.data)
    return JSONResponse({"status": "ok"})


@router.get("/api/webhook-url")
async def get_webhook_url():
    from backend.config import settings
    return JSONResponse({"url": settings.N8N_WEBHOOK_URL})


@router.get("/tab/portfolio", response_class=HTMLResponse)
async def portfolio_view(request: Request):
    properties = get_all_properties()
    return templates.TemplateResponse(
        request=request,
        name="partials/portfolio.html",
        context={"properties": properties},
    )
