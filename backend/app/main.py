from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.scraper.site_cloner import scrape_website
from pydantic import BaseModel

app = FastAPI()

class CloneRequest(BaseModel):
    url: str

@app.post("/clone")
async def clone_website(request: CloneRequest) -> Dict[str, Any]:
    try:
        result = await scrape_website(request.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"message": "Welcome to the LLM-powered website cloner API"}



class CloneRequest(BaseModel):
    url: str

@app.post("/clone")
async def clone_site(request: CloneRequest):
    from app.scraper.llm_cloner import scrape_website
    try:
        result = await scrape_website(request.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

