import uuid
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends

# Import services
from src.services.document_service import DocumentService, get_document_service
from src.services.gemini_service import GeminiService, get_gemini_service
from src.services.analysis_service import AnalysisService, get_analysis_service
from src.core.database import get_db_session, AnalysisSession

# Import models
from src.core.models import AnalysisRequest, AnalysisResponse

# Import logging
from src.utils.logging_utils import get_app_logger

# Initialize logger
logger = get_app_logger()

router = APIRouter()

@router.post("/", response_model=AnalysisResponse)
async def analyze_documents(
    request: AnalysisRequest,
    document_service: DocumentService = Depends(get_document_service),
    db_session = Depends(get_db_session)
):
    """Create a document session without analysis"""
    try:
        # Check if all documents exist
        for doc_id in request.document_ids:
            if not document_service.document_exists(doc_id):
                raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
        
        # Collect documents
        documents = [document_service.get_document(doc_id) for doc_id in request.document_ids]
        
        # Generate a unique ID for the session
        analysis_id = str(uuid.uuid4())
        
        # Create a default summary
        summary = f"Document session with {len(documents)} document(s)"
        
        # Create a new session in the database
        new_session = AnalysisSession(
            analysis_id=analysis_id,
            summary=summary,
            context=request.query,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Add documents to the session
        for doc in documents:
            new_session.documents.append(doc)
        
        # Save to database
        db_session.add(new_session)
        db_session.commit()
        
        # Return response
        return {
            "analysis_id": analysis_id,
            "summary": summary,
            "insights": [],  # Empty insights since no analysis is performed
            "document_count": len(documents)
        }
        
    except Exception as e:
        logger.error(f"Error creating document session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating document session: {str(e)}")

@router.get("/sessions", response_model=Dict[str, Any])
async def get_analysis_sessions(
    document_service: DocumentService = Depends(get_document_service)
):
    """Get all document sessions"""
    try:
        # Get sessions from database
        db = get_db_session()
        db_sessions = db.query(AnalysisSession).all()
        
        sessions = []
        for session in db_sessions:
            # Format documents
            documents = [
                {
                    "document_id": doc.id,
                    "file_name": doc.file_name
                }
                for doc in session.documents
            ]
            
            # Create session with required fields
            session_data = {
                "analysis_id": session.id,
                "created_at": session.created_at.isoformat(),
                "documents": documents,
                "summary": session.summary or "No summary available"
            }
            sessions.append(session_data)
            
        return {"sessions": sessions}
    except Exception as e:
        logger.error(f"Error in get_document_sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}", response_model=Dict[str, Any])
async def get_analysis_session(
    session_id: str
):
    """Get a specific document session by ID"""
    try:
        # Get session from database
        db = get_db_session()
        session = db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
        
        if not session:
            raise HTTPException(status_code=404, detail=f"Document session {session_id} not found")
        
        # Format documents
        documents = [
            {
                "document_id": doc.id,
                "file_name": doc.file_name
            }
            for doc in session.documents
        ]
        
        # Create session response
        session_data = {
            "analysis_id": session.id,
            "created_at": session.created_at.isoformat(),
            "documents": documents,
            "summary": session.summary or "No summary available",
            "context": session.context
        }
            
        return session_data
    except Exception as e:
        logger.error(f"Error in get_document_session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/documents", response_model=Dict[str, Any])
async def get_session_documents(
    session_id: str,
    document_service: DocumentService = Depends(get_document_service)
):
    """Get documents for a specific document session"""
    try:
        # Get session from database
        db = get_db_session()
        session = db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
        
        if not session:
            raise HTTPException(status_code=404, detail=f"Document session {session_id} not found")
        
        # Get documents from the session
        documents = []
        for doc in session.documents:
            # Format document for response
            documents.append({
                "document_id": doc.id,
                "filename": doc.file_name,
                "title": doc.metadata.get("title", doc.file_name) if doc.metadata else doc.file_name,
                "mime_type": doc.mime_type,
                "created_at": doc.created_at.isoformat()
            })
        
        return {"documents": documents}
    except Exception as e:
        logger.error(f"Error in get_session_documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/chat_history", response_model=Dict[str, Any])
async def get_session_chat_history(
    session_id: str
):
    """Get chat history (queries and responses) for a specific session"""
    try:
        # Get session from database
        db = get_db_session()
        session = db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
        
        if not session:
            raise HTTPException(status_code=404, detail=f"Document session {session_id} not found")
        
        # Get all queries for this session
        queries = session.queries
        
        # Format the chat history
        chat_history = []
        for query in queries:
            chat_history.append({
                "query_id": query.id,
                "query_text": query.query_text,
                "response_text": query.response_text,
                "created_at": query.created_at.isoformat()
            })
        
        return {"chat_history": chat_history}
    except Exception as e:
        logger.error(f"Error in get_session_chat_history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))