from playwright.async_api import async_playwright
import base64
from urllib.parse import urljoin
import re

async def intelligent_clone(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(url, wait_until="networkidle")

        # Inline styles
        await page.add_script_tag(content="""
            (async () => {
              const links = [...document.querySelectorAll('link[rel="stylesheet"]')];
              for (const link of links) {
                try {
                  const href = link.href;
                  const res = await fetch(href);
                  const css = await res.text();
                  const style = document.createElement('style');
                  style.textContent = css;
                  link.replaceWith(style);
                } catch (e) {}
              }
            })();
        """)

        # Fix relative paths
        await page.evaluate(f"""
            () => {{
                const fix = (attr) => {{
                    document.querySelectorAll(`[${{attr}}]`).forEach(el => {{
                        const val = el.getAttribute(attr);
                        if (val && val.startsWith('/')) {{
                            el.setAttribute(attr, new URL(val, '{url}').href);
                        }}
                    }});
                }};
                fix('src');
                fix('href');
            }}
        """)

        html = await page.content()
        screenshot = await page.screenshot(type='png')

        # Extract simple design context
        title = await page.title()
        has_nav = await page.query_selector("nav") is not None
        has_header = await page.query_selector("header") is not None
        has_main = await page.query_selector("main") is not None

        await browser.close()

        return {
            "success": True,
            "title": title,
            "html": html,
            "screenshot_base64": base64.b64encode(screenshot).decode(),
            "layout": {
                "has_nav": has_nav,
                "has_header": has_header,
                "has_main": has_main,
            }
        }
