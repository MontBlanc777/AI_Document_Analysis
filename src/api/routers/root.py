from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

def get_templates(request: Request):
    """Dependency to get templates from app state"""
    return request.app.state.templates

@router.get("/", response_class=HTMLResponse)
async def root(request: Request, templates: Jinja2Templates = Depends(get_templates)):
    """Root endpoint that serves the main HTML page"""
    return templates.TemplateResponse("index.html", {"request": request})