# backend/app/scraper.py

from typing import Dict

async def scrape_website(url: str) -> Dict:
    """
    Placeholder scraper function.
    Later, this will use Playwright to extract design context.
    """
    return {
        "url": url,
        "title": "Placeholder Title",
        "colors": ["#111827", "#1F2937"],
        "fonts": ["Inter", "sans-serif"],
        "framework": "Tailwind",
        "screenshot_base64": "",
        "success": True
    }
