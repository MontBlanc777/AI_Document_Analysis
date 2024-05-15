import os
import uuid
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import Depends, Request

from src.core.document_processor import DocumentProcessor
from src.services.gemini_service import GeminiService
from src.core.database import get_db_session, Document, DocumentContent
from src.utils.logging_utils import get_app_logger

# Initialize logger
logger = get_app_logger()

class DocumentService:
    """Service for managing documents"""
    
    def __init__(self, upload_folder: str):
        """Initialize the document service"""
        self.upload_folder = upload_folder
        self.document_processor = DocumentProcessor(upload_folder)
        self.db = get_db_session()
        logger.info(f"DocumentService initialized with upload folder: {upload_folder}")
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save an uploaded file and return the file path"""
        logger.info(f"Saving uploaded file: {filename}, size: {len(file_content)} bytes")
        try:
            file_path = self.document_processor.save_uploaded_file(file_content, filename)
            logger.info(f"File saved successfully: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to save file {filename}: {str(e)}")
            raise
        
    def process_url(self, url: str) -> dict:
        """Process a URL and return document information"""
        try:
            # Validate URL
            if not self.document_processor.is_valid_url(url):
                logger.warning(f"Invalid URL format: {url}")
                return {"status": "error", "error": "Invalid URL format"}
                
            # Process URL
            logger.info(f"Processing URL: {url}")
            file_path, filename, mime_type = self.document_processor.process_url(url)
            
            # Generate document ID
            document_id = str(uuid.uuid4())
            
            logger.info(f"URL processed successfully: {url}, saved as {file_path}")
            return {
                "status": "success", 
                "document_id": document_id,
                "file_path": file_path,
                "file_name": filename,
                "mime_type": mime_type
            }
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def get_mime_type(self, filename: str) -> str:
        """Get the MIME type of a file"""
        return self.document_processor.get_mime_type(filename)
    
    async def process_document(self, file_path: str, file_name: str, mime_type: str, document_id: str, gemini_service: GeminiService):
        """Process a document and store its information in the database"""
        try:
            logger.info(f"Processing document: {file_name}, ID: {document_id}")
            
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"File not found for processing: {file_path}")
                return {"status": "error", "document_id": document_id, "error": "File not found"}
            
            # Process the document using DocumentProcessor
            document_info = self.document_processor.process_document(file_path)
            
            # Extract text content based on file type
            extracted_text = ""
            if "text_content" in document_info:
                extracted_text = document_info["text_content"]
            elif "content" in document_info:
                extracted_text = document_info["content"]
            elif "slides" in document_info:
                # For PowerPoint, join all slide text
                extracted_text = "\n\n".join(document_info["slides"])
            elif "sheets" in document_info:
                # For Excel, convert sheet data to text
                sheet_texts = []
                for sheet_name, sheet_data in document_info["sheets"].items():
                    sheet_text = f"Sheet: {sheet_name}\n"
                    for row in sheet_data:
                        sheet_text += "\t".join([str(cell) if cell is not None else "" for cell in row]) + "\n"
                    sheet_texts.append(sheet_text)
                extracted_text = "\n\n".join(sheet_texts)
            elif "body" in document_info:
                # For emails
                extracted_text = document_info["body"]
            # For PDF files, we need to handle the case where only images are extracted
            elif "mime_type" in document_info and document_info["mime_type"] == "application/pdf":
                # For PDFs, use metadata or file info as fallback
                extracted_text = f"PDF Document: {file_name}\n\n"
                # Add any available metadata
                if "metadata" in document_info:
                    extracted_text += "Metadata:\n"
                    for key, value in document_info["metadata"].items():
                        extracted_text += f"{key}: {value}\n"
                # Note about image extraction
                if "extracted_images" in document_info:
                    extracted_text += f"\nNote: {len(document_info['extracted_images'])} images were extracted from this PDF."
                    extracted_text += "\nText extraction is limited for this PDF document."
            
            # Log the extracted text length
            logger.info(f"Extracted text length for {file_name}: {len(extracted_text)}")
            
            # Store document information in the database
            # Create the main document record
            document = Document(
                id=document_id,
                file_name=file_name,
                mime_type=mime_type,
                file_path=file_path,
                doc_metadata=json.dumps(document_info),
                status='uploaded',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Create the document content record - store full text without limits
            document_content = DocumentContent(
                id=document_id,
                analysis=None,  # No analysis needed for chat mode
                extracted_text=extracted_text
            )
            
            self.db.add(document)
            self.db.add(document_content)
            self.db.commit()
            
            logger.info(f"Document processed and saved successfully: {document_id}")
            return {"status": "success", "document_id": document_id}
        except Exception as e:
            logger.error(f"Error processing document {document_id}: {str(e)}")
            self.db.rollback()
            return {"status": "error", "document_id": document_id, "error": str(e)}
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents"""
        logger.info("Listing all documents")
        documents = self.db.query(Document).all()
        return [
            {
                "document_id": doc.id,
                "file_name": doc.file_name,
                "mime_type": doc.mime_type,
                "status": doc.status,
                "created_at": doc.created_at.isoformat(),
                "updated_at": doc.updated_at.isoformat(),
            }
            for doc in documents
        ]
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID"""
        logger.info(f"Getting document: {document_id}")
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.warning(f"Document not found: {document_id}")
            return None
        
        # Get document content if available
        document_content = self.db.query(DocumentContent).filter(DocumentContent.id == document_id).first()
        analysis = None
        extracted_text = None
        if document_content:
            analysis = document_content.analysis
            extracted_text = document_content.extracted_text
            
        return {
            "document_id": document.id,
            "file_name": document.file_name,
            "mime_type": document.mime_type,
            "file_path": document.file_path,
            "status": document.status,
            "analysis": analysis,
            "extracted_text": extracted_text,
            "metadata": json.loads(document.doc_metadata) if document.doc_metadata else {},
            "created_at": document.created_at.isoformat(),
            "updated_at": document.updated_at.isoformat(),
        }
    
    def document_exists(self, document_id: str) -> bool:
        """Check if a document exists"""
        return self.db.query(Document).filter(Document.id == document_id).count() > 0
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document"""
        logger.info(f"Deleting document: {document_id}")
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.warning(f"Document not found for deletion: {document_id}")
            return False
        
        # Get file path before deleting from database
        file_path = document.file_path
        
        # Remove from database
        self.db.delete(document)
        self.db.commit()
        
        # Delete the file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")
            else:
                logger.warning(f"File not found for deletion: {file_path}")
        except Exception as e:
            # Log the error but don't fail the request
            logger.error(f"Error deleting file {file_path}: {str(e)}")
        
        return True

# Dependency for getting the document service
def get_document_service(request: Request) -> DocumentService:
    """Dependency to get the document service"""
    # Get upload folder from environment or use default
    upload_folder = os.getenv("UPLOAD_FOLDER", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads"))

    upload_folder="./uploads"
    logger.info(f"Using upload folder: {upload_folder}")
    return DocumentService(upload_folder)