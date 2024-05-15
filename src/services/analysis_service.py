import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from fastapi import Depends

from src.core.database import get_db_session, AnalysisSession, Document, DocumentContent, Query
from src.utils.logging_utils import get_app_logger

# Initialize logger
logger = get_app_logger()

# Service for managing document analysis
class AnalysisService:
    def __init__(self):
        pass
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get a specific document session"""
        logger.info(f"Getting document session: {session_id}")
        db = get_db_session()
        session = db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
        
        if not session:
            logger.warning(f"Document session not found: {session_id}")
            return None
        
        # Format the session data
        documents = [
            {
                "document_id": doc.id,
                "file_name": doc.file_name,
                "status": doc.status
            }
            for doc in session.documents
        ]
        
        return {
            "analysis_id": session.id,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "context": session.context,
            "summary": session.summary,
            "documents": documents
        }

# Dependency for getting the analysis service
def get_analysis_service():
    return AnalysisService()