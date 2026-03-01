from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.services.parser import run_parsing_pipeline

router = APIRouter()


class ParseRequest(BaseModel):
    text: str


@router.post("/parse")
async def parse_listing(req: ParseRequest):
    """Parse a raw property listing into structured 15-field JSON.

    Returns a Server-Sent Events stream with step-by-step progress.
    """
    return StreamingResponse(
        run_parsing_pipeline(req.text),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
