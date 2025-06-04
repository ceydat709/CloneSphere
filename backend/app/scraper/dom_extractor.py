# app/scraper/browser_extractor.py

from typing import List, Dict, Any
from playwright.async_api import Page

async def extract_dom_layout(page: Page) -> List[Dict[str, Any]]:
    return await page.evaluate(
        """
        () => {
            const tags = ['header', 'nav', 'main', 'section', 'footer', 'article'];
            return Array.from(document.querySelectorAll(tags.join(','))).map(el => {
                const rect = el.getBoundingClientRect();
                const styles = getComputedStyle(el);
                return {
                    tag: el.tagName.toLowerCase(),
                    text: el.innerText.slice(0, 100),
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height,
                    visible: styles.display !== 'none' && styles.visibility !== 'hidden',
                    background: styles.backgroundColor,
                    font: styles.fontFamily,
                };
            });
        }
        """
    )
