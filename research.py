"""Source-linked web research. Search results and page contents are untrusted evidence."""
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup

async def research(query: str, limit: int = 6) -> dict:
    query=query.strip()
    if not query: raise ValueError("Research query cannot be blank")
    async with httpx.AsyncClient(timeout=20,follow_redirects=True,headers={"User-Agent":"ORBIT-Research/1.0"}) as client:
        response=await client.post("https://html.duckduckgo.com/html/",data={"q":query}); response.raise_for_status()
    soup=BeautifulSoup(response.text,"html.parser"); results=[]
    for item in soup.select(".result"):
        link=item.select_one(".result__a"); snippet=item.select_one(".result__snippet")
        if not link: continue
        url=link.get("href",""); parsed=urlparse(url)
        if parsed.scheme not in {"http","https"} or not parsed.hostname: continue
        results.append({"title":link.get_text(" ",strip=True)[:300],"url":url[:2000],
                        "snippet":snippet.get_text(" ",strip=True)[:1000] if snippet else ""})
        if len(results)>=max(1,min(limit,10)): break
    return {"query":query,"results":results,"note":"Search snippets are unverified; prefer primary sources and verify claims."}

async def open_page(url: str) -> dict:
    parsed=urlparse(url)
    if parsed.scheme!="https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Only absolute HTTPS URLs without embedded credentials are allowed")
    try: from playwright.async_api import async_playwright
    except ImportError as exc: raise RuntimeError("Install Playwright and Chromium to enable browser reading") from exc
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True); page=await browser.new_page()
        try:
            await page.goto(url,wait_until="domcontentloaded",timeout=20000)
            return {"url":page.url,"title":(await page.title())[:300],"text":(await page.locator("body").inner_text(timeout=5000))[:12000]}
        finally: await browser.close()
