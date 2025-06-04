from fastapi import HTTPException
from playwright.async_api import async_playwright
from .dom_extractor import extract_dom_layout
from .html_analyzer import extract_design_context
import base64

async def scrape_website(url: str) -> dict:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url)

            title = await page.title()
            content = await page.content()

            screenshot_bytes = await page.screenshot(type='png')
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode()

            await browser.close()

            # Extract structured info from HTML
            layout_info = extract_dom_layout(content)
            design_info = await extract_design_context(content)

            return {
                "url": url,
                "title": title,
                "screenshot_base64": screenshot_base64,
                "layout": layout_info,
                **design_info,
                "success": True,
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping website: {str(e)}")
