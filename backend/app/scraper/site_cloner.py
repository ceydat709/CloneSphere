from app.scraper.intelligent_scraper import intelligent_clone

async def scrape_website(url: str):
    return await intelligent_clone(url)
