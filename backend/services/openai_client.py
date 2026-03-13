import json

from src.core.logger import get_logger

from openai import AzureOpenAI

from backend.config import settings
from backend.schemas.property import PROPERTY_JSON_SCHEMA

log = get_logger(__name__)

SYSTEM_PROMPT = """You are a strict parser for multifamily property listings.

From the provided RAW TEXT, extract and normalize fields into EXACTLY this JSON schema (keys and order must match, no extras).

NORMALIZATION RULES:
- Currency: prefix with "$", thousands separators, no decimals unless present in source (e.g., "$1,234,567.89").
- Percentages: keep one or two decimals if present and include "%".
- Dates: ISO format YYYY-MM-DD. If only "Last Updated" and no "Date on Market", use first published/list date; if unknown, set to null.
- Address: street number + street name only (no city/state/ZIP).
- City: format as "City, ST ZIP".
- Lot/building size: format as "X SF / Y SF" with " / " separator. If either is missing, include what you know and "unknown" for the other.
- Total Units: integer extracted from listing (e.g., "6-unit" -> 6).
- Unit Mix Summary: summarize each unit type using ACTUAL rents as "QTYxBD/BA@$RENT", separated by " | ". Use average actual rent for grouped units. Vacant units show @$0.
- Description: one factual sentence, <=200 chars, no marketing phrases.

PROJECTED vs ACTUAL Rent:
- "Monthly Rental Income (Projected)": scheduled/asking rent from listing. If only annual projected, derive with /12.
- "Annual Rent Income (Projected)": scheduled/asking annual rent, or derive from monthly x 12.
- "Monthly Rental Income (Actual)": actual/current rent. Sum all units' actual rents. If only annual actual, derive with /12. If no actual rent data, set to null.
- "Annual Rent Income (Actual)": actual/current annual rent. If only monthly actual, derive with x12. If no actual rent data, set to null.
- Vacant units have $0 actual rent.

NOI: Prefer stated NOI. If absent but EGI and expenses are present, compute NOI = EGI - Expenses. If not computable, set to null.

NEVER fabricate values. If you cannot determine a field from the text, set it to null."""

ENRICHMENT_PROMPT = """You are re-extracting property data with additional context.

The first pass extracted some fields. You now have enrichment data:
- Rentcast rent estimates (if provided)
- A listing URL (if found)

Merge the enrichment data with the original extraction. Rules:
- RENTCAST DATA = actual market rents for the area. Place Rentcast values into
  Monthly Rental Income (Actual) and Annual Rent Income (Actual), NOT Projected.
  Keep any listing-provided Projected rents unchanged.
- If a listing URL was found and the first pass had null for Link, use the found URL.
- Keep all other fields from the first pass unless the enrichment data provides a clearly better value.
- All the same normalization rules apply."""


def _get_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version="2024-10-21",
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    )


def extract_fields(raw_text: str, url: str | None = None) -> dict:
    """First-pass extraction: raw text -> 15-field JSON via structured output."""
    client = _get_client()

    user_content = f"RAW TEXT:\n{raw_text}"
    if url:
        user_content += f"\n\nLISTING URL: {url}"

    response = client.chat.completions.create(
        model=settings.AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "property_data",
                "strict": True,
                "schema": PROPERTY_JSON_SCHEMA,
            },
        },
        temperature=0.0,
    )

    content = response.choices[0].message.content
    return json.loads(content)


def enrich_and_reextract(
    raw_text: str,
    first_pass: dict,
    rentcast_data: dict | None = None,
    found_url: str | None = None,
) -> dict:
    """Second pass: re-extract with enrichment context (Rentcast data, found URL)."""
    client = _get_client()

    enrichment_parts = [f"FIRST PASS RESULT:\n{json.dumps(first_pass, indent=2)}"]

    if rentcast_data:
        # Label matches the prompt instruction: Rentcast = actual market rents
        enrichment_parts.append(
            f"RENTCAST MARKET RENT DATA:\n{json.dumps(rentcast_data, indent=2)}"
        )

    if found_url:
        enrichment_parts.append(f"FOUND LISTING URL: {found_url}")

    user_content = (
        f"RAW TEXT:\n{raw_text}\n\n" + "\n\n".join(enrichment_parts)
    )

    response = client.chat.completions.create(
        model=settings.AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": ENRICHMENT_PROMPT},
            {"role": "user", "content": user_content},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "property_data",
                "strict": True,
                "schema": PROPERTY_JSON_SCHEMA,
            },
        },
        temperature=0.0,
    )

    content = response.choices[0].message.content
    return json.loads(content)
