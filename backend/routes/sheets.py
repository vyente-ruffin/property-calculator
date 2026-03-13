"""Routes for saving/retrieving properties via Google Sheets."""

from __future__ import annotations

from src.core.logger import get_logger

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.sheets import SheetsNotConfiguredError, SheetsService

router = APIRouter(tags=["sheets"])
log = get_logger("sheets")


class SaveRequest(BaseModel):
    """Accepts arbitrary property data to append to the sheet."""

    data: dict


@router.post("/properties")
async def save_property(req: SaveRequest):
    """Append a property row to Google Sheets."""
    try:
        svc = SheetsService()
    except SheetsNotConfiguredError:
        log.error("google_sheets_not_configured")
        raise HTTPException(status_code=503, detail="Google Sheets not configured") from None
    row = svc.append_property(req.data)
    log.info("google_sheet_row_appended row=%s price=%s state=%s", row, req.data.get("purchase_price"), req.data.get("state"))
    return {"status": "saved", "row": row}


@router.get("/properties")
async def list_properties():
    """Return all saved properties with portfolio summary."""
    try:
        svc = SheetsService()
    except SheetsNotConfiguredError:
        raise HTTPException(status_code=503, detail="Google Sheets not configured") from None
    records = svc.get_all_properties()
    summary = svc.get_summary()
    return {"properties": records, "summary": summary}
