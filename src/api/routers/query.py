import uuid
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
import logging

# Import services
from src.services.document_service import DocumentService, get_document_service
from src.services.gemini_service import GeminiService, get_gemini_service
from src.core.database import get_db_session
from src.utils.logging_utils import get_app_logger

# Import models
from src.core.models import QueryResponse

# Initialize logger
logger = get_app_logger()

router = APIRouter()

@router.post("/", response_model=QueryResponse)
async def query_documents(
    request: dict,
    document_service: DocumentService = Depends(get_document_service),
    gemini_service: GeminiService = Depends(get_gemini_service)
):
    """Chat with documents directly without requiring a session"""
    try:
        # Extract document IDs and query from request
        document_ids = request.get("document_ids", [])
        query = request.get("query", "")
        
        logger.info(f"Processing query with {len(document_ids)} documents")
        
        if not document_ids:
            raise HTTPException(status_code=400, detail="No documents selected")
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        # Collect documents
        documents = []
        for doc_id in document_ids:
            document = document_service.get_document(doc_id)
            if not document:
                logger.error(f"Document {doc_id} not found")
                raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
            documents.append(document)
        
        # Create a structured prompt for Gemini with improved analysis logic
        system_prompt = (
            "You are an AI assistant specialized in document analysis and question answering. "
            "Your task is to provide accurate, concise answers based solely on the content of the provided documents. "
            "Follow these guidelines:\n"
            "1. Only use information explicitly stated in the documents\n"
            "2. If the answer is not in the documents, say so clearly\n"
            "3. Cite specific document names when referencing information\n"
            "4. Provide direct quotes when appropriate\n"
            "5. Structure complex answers with bullet points or numbered lists\n"
            "6. Format code snippets, tables, and technical content appropriately\n"
        )
        
        # Add document context with clear separation and metadata
        document_context = ""
        for i, doc in enumerate(documents):
            doc_id = doc.get("document_id")
            doc_name = doc.get("file_name")
            doc_content = doc.get("extracted_text", "")
            
            # Log document content information
            content_length = len(doc_content) if doc_content else 0
            logger.info(f"Document {doc_name} (ID: {doc_id}) content length: {content_length}")
            
            if not doc_content:
                logger.warning(f"No content extracted for document: {doc_name} (ID: {doc_id})")
            
            if doc_content:
                document_context += f"\n\n--- DOCUMENT {i+1}: {doc_name} (ID: {doc_id}) ---\n{doc_content}\n"
        
        if not document_context.strip():
            logger.error("No document content available for query")
            return {
                "response": "I couldn't find any content in the selected documents. Please try with different documents or check if the documents were processed correctly.",
                "sources": [{
                    "document_id": doc.get("document_id"), 
                    "file_name": doc.get("file_name")
                } for doc in documents],
                "created_at": datetime.now().isoformat(),
            }
        
        # Construct the final prompt with clear sections
        prompt = f"{system_prompt}\n\nDOCUMENT CONTENT:\n{document_context}\n\nUSER QUERY: {query}\n\nPlease provide a comprehensive answer based only on the information in the documents above."
        
        # Log prompt length
        logger.info(f"Generated prompt with length: {len(prompt)}")
        
        # Generate response with Gemini
        response_text = await gemini_service.generate_content(prompt)
        
        # Format sources from documents
        sources = [
            {"document_id": doc.get("document_id"), "file_name": doc.get("file_name")} 
            for doc in documents
        ]
        
        return {
            "response": response_text,
            "sources": sources,
            "created_at": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))