import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, File, UploadFile, BackgroundTasks, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import services
from src.services.document_service import DocumentService, get_document_service
from src.services.gemini_service import GeminiService, get_gemini_service

# Import models
from src.core.models import DocumentResponse, DocumentListResponse, UrlRequest
from src.core.database import get_db_session, Document

# Import logging
from src.utils.logging_utils import get_app_logger

# Initialize logger
logger = get_app_logger()

router = APIRouter()

@router.post("/", response_model=Dict[str, Any])
@router.post("/upload", response_model=Dict[str, Any])
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_service: DocumentService = Depends(get_document_service),
    gemini_service: GeminiService = Depends(get_gemini_service),
    db: Session = Depends(get_db_session)
):
    """Upload a document for processing"""
    try:
        logger.info(f"Document upload request received: {file.filename}")
        
        # Generate a unique ID for the document
        document_id = str(uuid.uuid4())
        logger.info(f"Generated document ID: {document_id}")
        
        # Save the file
        file_content = await file.read()
        logger.info(f"Read file content: {len(file_content)} bytes")
        
        try:
            file_path = document_service.save_uploaded_file(file_content, file.filename)
            logger.info(f"File saved at: {file_path}")
        except Exception as save_error:
            logger.error(f"Failed to save file {file.filename}: {str(save_error)}")
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": f"Failed to save file: {str(save_error)}"}
            )
        
        # Get MIME type
        mime_type = document_service.get_mime_type(file.filename)
        
        # Process the document in the background
        logger.info(f"Starting background processing for document: {document_id}")
        background_tasks.add_task(
            document_service.process_document,
            file_path, 
            file.filename, 
            mime_type, 
            document_id,
            gemini_service
        )
        
        logger.info(f"Document upload successful: {document_id}")
        return {"success": True, "document_id": document_id, "status": "uploaded", "message": "Document uploaded successfully."}
    except Exception as e:
        logger.error(f"Error in upload_document: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@router.post("/url", response_model=Dict[str, Any])
async def process_url(
    background_tasks: BackgroundTasks,
    request: UrlRequest,
    document_service: DocumentService = Depends(get_document_service),
    gemini_service: GeminiService = Depends(get_gemini_service),
    db: Session = Depends(get_db_session)
):
    """Process a URL and analyze its content"""
    try:
        # Process the URL
        result = document_service.process_url(str(request.url))
        
        if result["status"] == "error":
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": result["error"]}
            )
        
        # Process the document in the background (without auto-analysis)
        background_tasks.add_task(
            document_service.process_document,
            result["file_path"], 
            result["file_name"], 
            result["mime_type"], 
            result["document_id"],
            gemini_service
        )
        
        return {"success": True, "document_id": result["document_id"], "status": "uploaded", "message": "URL processed and document saved successfully."}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    document_service: DocumentService = Depends(get_document_service),
    db: Session = Depends(get_db_session)
):
    """List all uploaded documents"""
    documents = document_service.list_documents()
    return {"documents": documents}

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str, 
    document_service: DocumentService = Depends(get_document_service),
    db: Session = Depends(get_db_session)
):
    """Get information about a specific document"""
    document = document_service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.delete("/{document_id}")
async def delete_document(
    document_id: str, 
    document_service: DocumentService = Depends(get_document_service),
    db: Session = Depends(get_db_session)
):
    """Delete a document"""
    success = document_service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "success", "message": f"Document {document_id} deleted"}