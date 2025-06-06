from playwright.async_api import async_playwright
import base64

async def render_generated_html(html_content: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()
        
        await page.set_content(html_content, wait_until="networkidle")
        await page.wait_for_timeout(1000)  # Give time for styles to settle

        screenshot = await page.screenshot(full_page=True)
        await browser.close()
        
        return base64.b64encode(screenshot).decode()
