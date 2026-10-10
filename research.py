"""Source-linked web research with SSRF-resistant browser navigation."""
import asyncio
import ipaddress
import socket
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup


async def research(query: str, limit: int = 6) -> dict:
    query = query.strip()
    if not query:
        raise ValueError("Research query cannot be blank")
    async with httpx.AsyncClient(timeout=20, follow_redirects=True,
                                 headers={"User-Agent": "ORBIT-Research/1.0"}) as client:
        response = await client.post("https://html.duckduckgo.com/html/", data={"q": query})
        response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for item in soup.select(".result"):
        link = item.select_one(".result__a")
        snippet = item.select_one(".result__snippet")
        if not link:
            continue
        url = link.get("href", "")
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
            continue
        results.append({"title": link.get_text(" ", strip=True)[:300], "url": url[:2000],
                        "snippet": snippet.get_text(" ", strip=True)[:1000] if snippet else ""})
        if len(results) >= max(1, min(limit, 10)):
            break
    return {"query": query, "results": results,
            "note": "Search snippets are unverified; prefer primary sources and verify claims."}


def _assert_public_https(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Only absolute public HTTPS URLs without embedded credentials are allowed")
    hostname = parsed.hostname.rstrip(".").lower()
    if hostname in {"localhost", "localhost.localdomain"} or hostname.endswith((".localhost", ".local", ".internal")):
        raise ValueError("Local and internal hostnames are blocked")
    try:
        literal = ipaddress.ip_address(hostname)
        addresses = [literal]
    except ValueError:
        try:
            records = socket.getaddrinfo(hostname, parsed.port or 443, type=socket.SOCK_STREAM)
            addresses = [ipaddress.ip_address(record[4][0].split("%", 1)[0]) for record in records]
        except (OSError, ValueError, IndexError) as exc:
            raise ValueError("The hostname could not be resolved safely") from exc
    if not addresses or any(not address.is_global for address in addresses):
        raise ValueError("Browser access to private, loopback, link-local or reserved IP addresses is blocked")
    return url


async def open_page(url: str) -> dict:
    _assert_public_https(url)
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise RuntimeError("Install Playwright and Chromium to enable browser reading") from exc

    async def guard_route(route):
        try:
            _assert_public_https(route.request.url)
        except ValueError:
            await route.abort("blockedbyclient")
            return
        await route.continue_()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(accept_downloads=False)
        page = await context.new_page()
        await page.route("**/*", guard_route)
        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            if response is None:
                raise RuntimeError("Browser navigation returned no response")
            final_url = _assert_public_https(page.url)
            return {"url": final_url, "title": (await page.title())[:300],
                    "text": (await page.locator("body").inner_text(timeout=5000))[:12000]}
        finally:
            await context.close()
            await browser.close()
