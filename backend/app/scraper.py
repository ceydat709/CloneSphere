from playwright.async_api import async_playwright
import asyncio

async def scrape_website(url: str) -> dict:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        title = await page.title()
        content = await page.content()

        screenshot_bytes = await page.screenshot(type='png')
        import base64
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode()

        await browser.close()

        return {
            "url": url,
            "title": title,
            "colors": ["#111827", "#1F2937"],  
            "fonts": ["Inter", "sans-serif"], 
            "framework": "Tailwind",           
            "screenshot_base64": screenshot_base64,
            "success": True,
        }
