import re
from urllib.parse import quote

from src.core.logger import get_logger

import httpx

from backend.config import settings

log = get_logger(__name__)

RENTCAST_BASE_URL = "https://api.rentcast.io/v1/avm/rent/long-term"


def parse_unit_mix(unit_mix: str) -> list[tuple[int, int, int]]:
    """Parse unit mix string into [(qty, bedrooms, bathrooms), ...].

    Handles formats like:
    - "2x1BD/1BA | 3x2BD/1BA"
    - "4x1BD/1BA"
    - "2x2BD/1BA + 3x1BD/1BA"
    """
    units = []
    # Split by | or +
    parts = re.split(r'\s*[|+]\s*', unit_mix)
    for part in parts:
        part = part.strip()
        # Match patterns like "2x1BD/1BA" or "1xStudio"
        m = re.match(
            r'(\d+)\s*[x×]\s*(\d+)\s*BD\s*/\s*(\d+(?:\.\d+)?)\s*BA',
            part,
            re.IGNORECASE,
        )
        if m:
            qty = int(m.group(1))
            br = int(m.group(2))
            ba = int(float(m.group(3)))
            units.append((qty, br, ba))
        else:
            # Try studio format
            m_studio = re.match(r'(\d+)\s*[x×]\s*Studio', part, re.IGNORECASE)
            if m_studio:
                qty = int(m_studio.group(1))
                units.append((qty, 0, 1))
    return units


def extract_zip_from_city(city: str) -> str | None:
    """Extract ZIP code from city string like 'Los Angeles, CA 90015'."""
    m = re.search(r'(\d{5})', city)
    return m.group(1) if m else None


async def get_projected_rent(
    address: str, zip_code: str, unit_mix: list[tuple[int, int, int]]
) -> dict | None:
    """Call Rentcast API for each unique unit type and calculate projected rent.

    Returns dict with monthly_total, annual_total, and per-type breakdown,
    or None on failure.
    """
    if not settings.RENTCAST_API_KEY:
        log.warning("No RENTCAST_API_KEY configured")
        return None

    encoded_address = quote(address)
    results = []
    monthly_total = 0

    async with httpx.AsyncClient(timeout=15.0) as client:
        for qty, br, ba in unit_mix:
            url = (
                f"{RENTCAST_BASE_URL}"
                f"?address={encoded_address}"
                f"&zipCode={zip_code}"
                f"&bedrooms={br}"
                f"&bathrooms={ba}"
            )
            try:
                resp = await client.get(
                    url,
                    headers={
                        "Accept": "application/json",
                        "X-Api-Key": settings.RENTCAST_API_KEY,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                rent_low = data.get("rentRangeLow")
                if rent_low is not None:
                    rent_low = int(float(rent_low))
                    unit_monthly = qty * rent_low
                    monthly_total += unit_monthly
                    results.append({
                        "qty": qty,
                        "bedrooms": br,
                        "bathrooms": ba,
                        "rent_per_unit": rent_low,
                        "subtotal": unit_monthly,
                    })
                else:
                    log.warning(f"Rentcast returned no rentRangeLow for {br}BD/{ba}BA")
                    return None
            except httpx.HTTPError as e:
                log.error(f"Rentcast API error for {br}BD/{ba}BA: {e}")
                return None

    if not results:
        return None

    annual_total = monthly_total * 12
    return {
        "monthly_total": monthly_total,
        "annual_total": annual_total,
        "monthly_formatted": f"${monthly_total:,}",
        "annual_formatted": f"${annual_total:,}",
        "breakdown": results,
    }
