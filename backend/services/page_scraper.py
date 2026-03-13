import re

from src.core.logger import get_logger

import httpx

from backend.config import settings

log = get_logger(__name__)

MIN_CONTENT_LENGTH = 100

# Phrases that indicate a block/captcha page, not real property content
_BLOCK_PHRASES = {
    "your request could not be processed",
    "access denied",
    "please verify you are a human",
    "enable javascript and cookies",
}

# Domain → scraper routing
_APIFY_DOMAINS = {"themls.com"}
# Cloudflare (LoopNet), PerimeterX (Zillow), rate-limiting (Realtor.com)
_BRIGHTDATA_DOMAINS = {"loopnet.com", "zillow.com", "realtor.com"}


def _is_block_page(text: str) -> bool:
    """Detect anti-bot block pages that pass length checks but contain no property data."""
    lower = text.lower()
    return any(phrase in lower for phrase in _BLOCK_PHRASES)


async def scrape_listing_page(url: str) -> str | None:
    """Fetch a listing page and extract its text content.

    Routing: Bright Data domains → Bright Data (Apify fallback),
    Apify domains → Apify, others → httpx (Apify fallback).
    """
    if any(d in url for d in _BRIGHTDATA_DOMAINS):
        text = await _scrape_with_brightdata(url)
        if text and not _is_block_page(text):
            return text
        # Bright Data got blocked — fall back to Apify for JS rendering
        log.info("brightdata_blocked, falling back to apify url=%s", url)
        return await _scrape_with_apify(url)

    if any(d in url for d in _APIFY_DOMAINS):
        return await _scrape_with_apify(url)

    text = await _scrape_with_httpx(url)
    if text and len(text) >= MIN_CONTENT_LENGTH and not _is_block_page(text):
        return text

    log.info("httpx got insufficient content for %s, trying Apify", url)
    return await _scrape_with_apify(url)


async def _scrape_with_httpx(url: str) -> str | None:
    """Fetch page with httpx (no JS execution)."""
    try:
        async with httpx.AsyncClient(
            timeout=15.0, follow_redirects=True
        ) as client:
            resp = await client.get(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                },
            )
            resp.raise_for_status()
            return _html_to_text(resp.text)

    except httpx.HTTPError as e:
        log.error("httpx failed for %s: %s", url, e)
        return None


async def _scrape_with_apify(url: str) -> str | None:
    """Fetch JS-rendered page via Apify SuperScraper API."""
    token = settings.APIFY_API_TOKEN
    if not token:
        log.warning("No APIFY_API_TOKEN configured, cannot scrape JS pages")
        return None

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.get(
                "https://super-scraper-api.apify.actor/",
                params={"url": url, "json_response": "true"},
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
            data = resp.json()
            html = data.get("body", "")

        if not html:
            log.error("Apify returned empty body for %s", url)
            return None

        text = _html_to_text(html)
        if len(text) < MIN_CONTENT_LENGTH:
            log.error("Apify got insufficient content (%d chars) for %s", len(text), url)
            return None
        return text

    except httpx.HTTPError as e:
        log.error("Apify request failed for %s: %s", url, e)
        return None
    except (KeyError, ValueError) as e:
        log.error("Apify response parse error for %s: %s", url, e)
        return None


async def _scrape_with_brightdata(url: str) -> str | None:
    """Fetch Cloudflare-protected page via Bright Data Scraping Browser."""
    wss = settings.BRIGHTDATA_BROWSER_WSS
    if not wss:
        log.warning("No BRIGHTDATA_BROWSER_WSS configured")
        return None

    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as pw:
            browser = await pw.chromium.connect_over_cdp(wss)
            page = browser.contexts[0].pages[0] if browser.contexts and browser.contexts[0].pages else await browser.new_page()
            # domcontentloaded + fixed wait — networkidle hangs on sites with constant analytics
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(8000)
            html = await page.content()
            await browser.close()

        text = _html_to_text(html)
        if len(text) < MIN_CONTENT_LENGTH:
            log.error("Bright Data got insufficient content (%d chars) for %s", len(text), url)
            return None
        log.info("brightdata_scrape_ok url=%s chars=%d", url, len(text))
        return text

    except Exception as e:
        log.error("Bright Data scrape failed for %s: %s", url, e)
        return None


def _html_to_text(html: str) -> str:
    """Convert HTML to plain text by stripping tags and collapsing whitespace."""
    for tag in ("script", "style", "nav", "footer", "header", "noscript", "svg"):
        html = re.sub(
            rf"<{tag}[^>]*>.*?</{tag}>",
            " ",
            html,
            flags=re.DOTALL | re.IGNORECASE,
        )

    html = re.sub(r"<!--.*?-->", " ", html, flags=re.DOTALL)
    html = re.sub(r"<(?:br|p|div|h[1-6]|li|tr|td|th)[^>]*>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"<[^>]+>", " ", html)

    html = html.replace("&amp;", "&")
    html = html.replace("&lt;", "<")
    html = html.replace("&gt;", ">")
    html = html.replace("&quot;", '"')
    html = html.replace("&#39;", "'")
    html = html.replace("&nbsp;", " ")
    html = re.sub(r"&#\d+;", " ", html)
    html = re.sub(r"&\w+;", " ", html)

    lines = []
    for raw_line in html.split("\n"):
        cleaned = re.sub(r"[ \t]+", " ", raw_line).strip()
        if cleaned:
            lines.append(cleaned)

    return "\n".join(lines)
