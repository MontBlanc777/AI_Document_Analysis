from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime

class DocumentMetadata(BaseModel):
    file_name: str
    file_size: int
    file_type: str
    upload_date: str

class Document(BaseModel):
    id: str
    metadata: DocumentMetadata

class QueryRequest(BaseModel):
    document_ids: List[str] = Field(..., description="List of document IDs to query")
    query: str = Field(..., description="Question to ask about the documents")

class AnalysisRequest(BaseModel):
    document_ids: List[str] = Field(..., description="List of document IDs to analyze")
    context: Optional[str] = Field(None, description="Optional context for the analysis")

class AnalysisInsight(BaseModel):
    type: str
    content: str

class AnalysisResponse(BaseModel):
    analysis_id: str
    summary: str
    insights: List[Dict[str, Any]]
    created_at: str

class DocumentSource(BaseModel):
    document_id: str
    file_name: str

class QueryResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]
    created_at: str

# Response Models
class DocumentInfo(BaseModel):
    document_id: str
    file_name: str
    mime_type: str
    created_at: str
    status: Optional[str] = None

class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo]

class DocumentResponse(BaseModel):
    document_id: str
    file_name: str
    mime_type: str
    analysis: str
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str
    status: Optional[str] = None

class UrlRequest(BaseModel):
    url: HttpUrl = Field(..., description="URL to process and analyze")