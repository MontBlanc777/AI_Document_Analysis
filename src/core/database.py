import os
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Table, Index, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session

# Create the SQLAlchemy base
Base = declarative_base()

# Define the association table for many-to-many relationship between documents and analysis sessions
document_analysis_association = Table(
    'document_analysis_association',
    Base.metadata,
    Column('document_id', String(36), ForeignKey('documents.id', ondelete='CASCADE')),
    Column('analysis_id', String(36), ForeignKey('analysis_sessions.id', ondelete='CASCADE')),
    Index('idx_doc_analysis_assoc_doc_id', 'document_id'),
    Index('idx_doc_analysis_assoc_analysis_id', 'analysis_id')
)

class Document(Base):
    """Document model for storing document information"""
    __tablename__ = 'documents'
    
    id = Column(String(36), primary_key=True)
    file_name = Column(String(255), nullable=False, index=True)
    file_path = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False, index=True)
    doc_metadata = Column(Text, nullable=True)  # JSON serialized metadata
    status = Column(String(50), default='uploaded', nullable=False, index=True)  # uploaded, analyzed, error
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Relationship with analysis sessions
    analysis_sessions = relationship(
        "AnalysisSession",
        secondary=document_analysis_association,
        back_populates="documents",
        cascade="all, delete"
    )
    
    # Relationship with document content
    content = relationship("DocumentContent", uselist=False, back_populates="document", cascade="all, delete-orphan")

class DocumentContent(Base):
    """Document content model for storing large text content separately"""
    __tablename__ = 'document_contents'
    
    id = Column(String(36), ForeignKey('documents.id', ondelete='CASCADE'), primary_key=True)
    analysis = Column(Text, nullable=True)  # Moved from Document table
    extracted_text = Column(Text, nullable=True)  # For storing extracted text content
    
    # Relationship with document
    document = relationship("Document", back_populates="content")

class AnalysisSession(Base):
    """Analysis session model for storing analysis information"""
    __tablename__ = 'analysis_sessions'
    
    id = Column(String(36), primary_key=True)
    summary = Column(Text, nullable=True)
    context = Column(Text, nullable=True)  # The prompt context
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Relationship with documents
    documents = relationship(
        "Document",
        secondary=document_analysis_association,
        back_populates="analysis_sessions",
        cascade="all"
    )
    
    # Relationship with queries
    queries = relationship("Query", back_populates="analysis_session", cascade="all, delete-orphan")

class Query(Base):
    """Query model for storing user queries and responses"""
    __tablename__ = 'queries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String(36), ForeignKey('analysis_sessions.id', ondelete='CASCADE'), index=True)
    query_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Relationship with analysis session
    analysis_session = relationship("AnalysisSession", back_populates="queries")

# Database setup function
def get_db_engine():
    """Get the database engine"""
    # Get the database path from environment or use default
    db_path = os.getenv("DATABASE_PATH", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "mcp.db"))
    
    # Create the engine
    engine = create_engine(f"sqlite:///{db_path}")
    
    return engine

def init_db():
    """Initialize the database"""
    engine = get_db_engine()
    Base.metadata.create_all(engine)
    
def get_db_session() -> Session:
    """Get a database session"""
    engine = get_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()