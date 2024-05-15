import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import routers
from src.api.routers import documents, analysis, query

# Import services
from src.services.gemini_service import GeminiService

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    # Initialize FastAPI app
    app = FastAPI(
        title="Document Analysis AI Server", 
        description="AI server for document analysis using Gemini 2.5 Pro and MCP"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Get base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    # Mount static files directory for uploads
    upload_folder = os.getenv("UPLOAD_FOLDER", os.path.join(base_dir, "uploads"))
    os.makedirs(upload_folder, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=upload_folder), name="uploads")
    # Mount static files directory for CSS, JS, etc.
    static_folder = os.path.join(base_dir, "static")
    app.mount("/static", StaticFiles(directory=static_folder), name="static")
    
    # Initialize templates
    templates_folder = os.path.join(base_dir, "templates")
    templates = Jinja2Templates(directory=templates_folder)
    
    # Add templates to app state
    app.state.templates = templates
    
    # Initialize Gemini service
    gemini_service = GeminiService()
    app.state.gemini_service = gemini_service
    
    # Include routers
    app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
    app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
    app.include_router(query.router, prefix="/api/query", tags=["query"])
    
    # Add root route
    from src.api.routers.root import router as root_router
    app.include_router(root_router)
    
    return app