import re

from src.core.logger import get_logger

import httpx

log = get_logger(__name__)

DUCKDUCKGO_HTML_URL = "https://html.duckduckgo.com/html/"


async def search_listing_url(address: str, city: str | None = None) -> str | None:
    """Search for a property listing URL using DuckDuckGo HTML search.

    Returns the first matching URL from known listing sites, or None.
    """
    query_parts = [f'"{address}"']
    if city:
        # Extract just the city name (before comma)
        city_name = city.split(",")[0].strip()
        query_parts.append(city_name)
    query_parts.append(
        "property listing site:loopnet.com OR site:zillow.com OR site:crexi.com OR site:realtor.com"
    )
    query = " ".join(query_parts)

    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.post(
                DUCKDUCKGO_HTML_URL,
                data={"q": query},
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                },
            )
            resp.raise_for_status()
            html = resp.text

            # Extract URLs from DuckDuckGo results
            listing_domains = [
                "loopnet.com",
                "zillow.com",
                "crexi.com",
                "realtor.com",
                "redfin.com",
            ]
            urls = re.findall(r'href="(https?://[^"]+)"', html)
            for url in urls:
                if any(domain in url for domain in listing_domains):
                    # Clean DuckDuckGo redirect URLs
                    if "duckduckgo.com" in url:
                        uddg_match = re.search(r'uddg=([^&]+)', url)
                        if uddg_match:
                            from urllib.parse import unquote
                            url = unquote(uddg_match.group(1))
                    return url

    except httpx.HTTPError as e:
        log.error(f"Web search failed: {e}")

    return None
