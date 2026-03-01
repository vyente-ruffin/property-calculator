import logging
import re

import httpx

logger = logging.getLogger(__name__)

MIN_CONTENT_LENGTH = 100


async def scrape_listing_page(url: str) -> str | None:
    """Fetch a listing page and extract its text content.

    Tries a fast httpx fetch first. If the extracted text is too short
    (JS-rendered SPA), falls back to a headless Playwright browser.

    Returns plain text from the page body, or None on failure.
    """
    # Fast path: plain HTTP fetch
    text = await _scrape_with_httpx(url)
    if text and len(text) >= MIN_CONTENT_LENGTH:
        return text

    logger.info(f"httpx got insufficient content for {url}, falling back to Playwright")
    return await _scrape_with_playwright(url)


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
        logger.error(f"httpx failed for {url}: {e}")
        return None


async def _scrape_with_playwright(url: str) -> str | None:
    """Fetch page with headless Playwright (executes JS)."""
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 720},
            )
            page = await context.new_page()
            await page.add_init_script(
                'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            )
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(5000)
            text = await page.inner_text("body")
            await browser.close()

        # Collapse whitespace
        lines = []
        for line in text.split("\n"):
            line = re.sub(r"[ \t]+", " ", line).strip()
            if line:
                lines.append(line)
        text = "\n".join(lines)

        if len(text) < MIN_CONTENT_LENGTH:
            logger.error(f"Playwright got insufficient content ({len(text)} chars) for {url}")
            return None
        return text

    except Exception as e:
        logger.error(f"Playwright failed for {url}: {e}")
        return None


def _html_to_text(html: str) -> str:
    """Convert HTML to plain text by stripping tags and collapsing whitespace."""
    # Remove script, style, nav, footer, header tags and their content
    for tag in ("script", "style", "nav", "footer", "header", "noscript", "svg"):
        html = re.sub(
            rf"<{tag}[^>]*>.*?</{tag}>",
            " ",
            html,
            flags=re.DOTALL | re.IGNORECASE,
        )

    # Remove HTML comments
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.DOTALL)

    # Replace block-level tags with newlines
    html = re.sub(r"<(?:br|p|div|h[1-6]|li|tr|td|th)[^>]*>", "\n", html, flags=re.IGNORECASE)

    # Remove all remaining tags
    html = re.sub(r"<[^>]+>", " ", html)

    # Decode common HTML entities
    html = html.replace("&amp;", "&")
    html = html.replace("&lt;", "<")
    html = html.replace("&gt;", ">")
    html = html.replace("&quot;", '"')
    html = html.replace("&#39;", "'")
    html = html.replace("&nbsp;", " ")
    html = re.sub(r"&#\d+;", " ", html)
    html = re.sub(r"&\w+;", " ", html)

    # Collapse whitespace
    lines = []
    for line in html.split("\n"):
        line = re.sub(r"[ \t]+", " ", line).strip()
        if line:
            lines.append(line)

    return "\n".join(lines)
