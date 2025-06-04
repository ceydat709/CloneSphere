from typing import Dict
from bs4 import BeautifulSoup

async def extract_design_context(html: str) -> Dict:
    soup = BeautifulSoup(html, "html.parser")

    return {
        "layout": {
            "has_nav": bool(soup.find("nav")),
            "has_header": bool(soup.find("header")),
            "has_main": bool(soup.find("main")),
        },
        "important_elements": {
            "header": soup.find("header").text if soup.find("header") else "",
            "nav": soup.find("nav").text if soup.find("nav") else "",
            "main_sections": [s.text for s in soup.find_all("section")],
        },
    }
