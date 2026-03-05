import json
import logging
import re
import sys
from collections.abc import AsyncGenerator
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".ai" / "logging"))
from logger import get_logger

from backend.services.openai_client import enrich_and_reextract, extract_fields
from backend.services.page_scraper import scrape_listing_page
from backend.services.rentcast import (
    extract_zip_from_city,
    get_projected_rent,
    parse_unit_mix,
)
from backend.services.web_search import search_listing_url

log = get_logger("parser")


def _sse_event(step: str, status: str, data: dict | None = None) -> str:
    """Format a server-sent event."""
    payload = {"step": step, "status": status}
    if data is not None:
        payload["data"] = data
    return f"data: {json.dumps(payload)}\n\n"


def _parse_input(text: str) -> tuple[str, str | None, bool]:
    """Separate raw listing text from optional trailing URL.

    Returns (raw_text, url, is_url_only).
    """
    text = text.strip()
    tokens = text.split()
    # Single URL with no surrounding text
    if len(tokens) == 1 and re.match(r'https?://', tokens[0]):
        return "", tokens[0], True
    if tokens and re.match(r'https?://', tokens[-1]):
        url = tokens[-1]
        raw_text = text[: text.rfind(url)].strip()
        return raw_text, url, False
    return text, None, False


async def run_parsing_pipeline(text: str) -> AsyncGenerator[str, None]:
    """7-step async generator yielding SSE events."""

    # Step 1: Parse input
    yield _sse_event("parse_input", "running")
    try:
        raw_text, url, is_url_only = _parse_input(text)
        log.info("step_parse_input", has_url=url is not None, text_length=len(raw_text), is_url_only=is_url_only)
        yield _sse_event(
            "parse_input",
            "done",
            {"has_url": url is not None, "text_length": len(raw_text), "is_url_only": is_url_only},
        )
    except Exception as e:
        log.error("step_parse_input_failed", error=str(e))
        yield _sse_event("parse_input", "error", {"message": str(e)})
        return

    # Step 1.5: Scrape URL if input is a standalone URL
    if is_url_only:
        yield _sse_event("scrape_url", "running")
        try:
            scraped_text = await scrape_listing_page(url)
            if scraped_text:
                raw_text = scraped_text
                log.info("step_scrape_url", text_length=len(raw_text), url=url)
                yield _sse_event(
                    "scrape_url", "done", {"text_length": len(raw_text)}
                )
            else:
                yield _sse_event(
                    "scrape_url", "error", {"message": "Failed to scrape page content"}
                )
                return
        except Exception as e:
            log.error("step_scrape_failed", error=str(e), url=url)
            yield _sse_event("scrape_url", "error", {"message": str(e)})
            return
    else:
        yield _sse_event("scrape_url", "skipped", {"reason": "Not a standalone URL"})

    # Step 2: Extract fields via Azure OpenAI
    yield _sse_event("extract_fields", "running")
    try:
        first_pass = extract_fields(raw_text, url)
        log.info("step_extract_fields", fields_found=len([v for v in first_pass.values() if v]), price=first_pass.get("Price"), address=first_pass.get("Address"))
        yield _sse_event("extract_fields", "done", {"fields": first_pass})
    except Exception as e:
        log.error("step_extract_failed", error=str(e))
        yield _sse_event("extract_fields", "error", {"message": str(e)})
        return

    # Step 3: Search for listing URL if missing
    found_url = None
    if not first_pass.get("Link") and not url:
        yield _sse_event("search_link", "running")
        try:
            address = first_pass.get("Address")
            city = first_pass.get("City")
            if address:
                found_url = await search_listing_url(address, city)
                if found_url:
                    yield _sse_event(
                        "search_link", "done", {"url": found_url}
                    )
                else:
                    yield _sse_event("search_link", "done", {"url": None})
            else:
                yield _sse_event(
                    "search_link", "skipped", {"reason": "No address to search"}
                )
        except Exception as e:
            log.error("step_search_link_failed", error=str(e))
            yield _sse_event("search_link", "error", {"message": str(e)})
    else:
        yield _sse_event(
            "search_link", "skipped", {"reason": "Link already provided"}
        )

    # Step 4: Rentcast for projected rent
    rentcast_data = None
    projected_missing = first_pass.get("Monthly Rental Income (Projected)") is None
    unit_mix_str = first_pass.get("Unit Mix Summary")

    if projected_missing and unit_mix_str:
        yield _sse_event("rentcast", "running")
        try:
            units = parse_unit_mix(unit_mix_str)
            address = first_pass.get("Address")
            city = first_pass.get("City", "")
            zip_code = extract_zip_from_city(city)

            if units and address and zip_code:
                rentcast_data = await get_projected_rent(address, zip_code, units)
                if rentcast_data:
                    yield _sse_event("rentcast", "done", {"rent": rentcast_data})
                else:
                    yield _sse_event(
                        "rentcast", "done", {"message": "No rent data returned"}
                    )
            else:
                missing = []
                if not units:
                    missing.append("unit mix")
                if not address:
                    missing.append("address")
                if not zip_code:
                    missing.append("zip code")
                yield _sse_event(
                    "rentcast",
                    "skipped",
                    {"reason": f"Missing: {', '.join(missing)}"},
                )
        except Exception as e:
            log.error("step_rentcast_failed", error=str(e))
            yield _sse_event("rentcast", "error", {"message": str(e)})
    else:
        reason = "Projected rent already present" if not projected_missing else "No unit mix available"
        yield _sse_event("rentcast", "skipped", {"reason": reason})

    # Step 5: Re-extract with enrichment if new data found
    needs_reextract = rentcast_data is not None or found_url is not None
    if needs_reextract:
        yield _sse_event("reextract", "running")
        try:
            final_data = enrich_and_reextract(
                raw_text, first_pass, rentcast_data, found_url
            )
            yield _sse_event("reextract", "done", {"fields": final_data})
        except Exception as e:
            log.error("step_reextract_failed", error=str(e))
            yield _sse_event("reextract", "error", {"message": str(e)})
            final_data = first_pass
    else:
        yield _sse_event(
            "reextract", "skipped", {"reason": "No enrichment data to merge"}
        )
        final_data = first_pass

    # Step 6: Validate all 15 fields
    yield _sse_event("validate", "running")
    expected_fields = [
        "Price", "Address", "City", "Cap Rate", "Date On Market",
        "Monthly Rental Income (Projected)", "Monthly Rental Income (Actual)",
        "Annual Rent Income (Projected)", "Annual Rent Income (Actual)",
        "NOI", "Lot / building size", "Total Units", "Unit Mix Summary",
        "Link", "Description",
    ]
    missing = [f for f in expected_fields if f not in final_data]
    null_fields = [f for f in expected_fields if f in final_data and final_data[f] is None]
    yield _sse_event(
        "validate",
        "done",
        {"missing_keys": missing, "null_fields": null_fields, "valid": len(missing) == 0},
    )

    # Step 7: Complete
    log.info("pipeline_complete",
             price=final_data.get("Price"),
             address=final_data.get("Address"),
             city=final_data.get("City"),
             units=final_data.get("Total Units"),
             noi=final_data.get("NOI"),
             annual_rent=final_data.get("Annual Rent Income (Actual)"))
    yield _sse_event("complete", "done", {"result": final_data})
