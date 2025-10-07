from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os

from search_engine import SearchEngine

app = FastAPI(title="Advanced Search Engine", description="Search engine powered by DataForSEO and Google Ranking API")

# Create templates directory if it doesn't exist
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize search engine
search_engine = SearchEngine()

class SearchRequest(BaseModel):
    query: str
    location: Optional[str] = "United States"
    language: Optional[str] = "en"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with search interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/search", response_class=HTMLResponse)
async def search_form(
    request: Request,
    query: str = Form(...),
    location: str = Form("United States"),
    language: str = Form("en")
):
    """Handle form-based search requests"""
    if not query.strip():
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Please enter a search query"
        })
    
    try:
        results = await search_engine.search(query.strip(), location, language)
        summary = search_engine.get_search_summary(results)
        
        return templates.TemplateResponse("results.html", {
            "request": request,
            "query": query,
            "results": results,
            "summary": summary
        })
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"Search error: {str(e)}"
        })

@app.post("/api/search")
async def api_search(search_request: SearchRequest):
    """API endpoint for search requests"""
    try:
        results = await search_engine.search(
            search_request.query,
            search_request.location,
            search_request.language
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/summary/{query}")
async def api_summary(query: str, location: str = "United States", language: str = "en"):
    """API endpoint to get search summary"""
    try:
        results = await search_engine.search(query, location, language)
        summary = search_engine.get_search_summary(results)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def api_status():
    """Check status of all services"""
    try:
        service_status = search_engine.test_all_services()
        return {
            "status": "ok",
            "services": service_status,
            "all_services_ok": all(service_status.values())
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "services": {"dataforseo": False, "google_ranking": False, "web_crawler": False},
            "all_services_ok": False
        }

@app.get("/status", response_class=HTMLResponse)
async def status_page(request: Request):
    """Status page showing service connectivity"""
    try:
        service_status = search_engine.test_all_services()
        return templates.TemplateResponse("status.html", {
            "request": request,
            "services": service_status
        })
    except Exception as e:
        return templates.TemplateResponse("status.html", {
            "request": request,
            "error": str(e),
            "services": {"dataforseo": False, "google_ranking": False, "web_crawler": False}
        })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 