from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.scraper import scrape_website

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
