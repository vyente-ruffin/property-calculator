"""Routes for saving/retrieving properties via Google Sheets."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.sheets import SheetsNotConfiguredError, SheetsService

router = APIRouter(tags=["sheets"])


class SaveRequest(BaseModel):
    """Accepts arbitrary property data to append to the sheet."""

    data: dict


@router.post("/properties")
async def save_property(req: SaveRequest):
    """Append a property row to Google Sheets."""
    try:
        svc = SheetsService()
    except SheetsNotConfiguredError:
        raise HTTPException(status_code=503, detail="Google Sheets not configured") from None
    row = svc.append_property(req.data)
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
