"""
Document model
"""
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID

from .base import BaseSQLModel


class DocumentStatus(str, Enum):
    """Document processing status enumeration"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"


class Document(SQLModel, BaseSQLModel, table=True):
    """Document model with database fields"""
    
    __tablename__ = "documents"
    
    filename: str = Field(description="Stored filename (system-generated)")
    original_name: str = Field(description="Original upload filename")
    size: int = Field(description="File size in bytes")
    mime_type: str = Field(description="MIME type of the file")
    status: DocumentStatus = Field(description="Document processing status")
    processed_at: Optional[datetime] = Field(
        default=None,
        description="Processing completion timestamp"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if processing failed"
    )
    
    # Add tenant_id and user_id for multi-tenancy
    tenant_id: UUID = Field(index=True, description="Tenant ID")
    user_id: UUID = Field(index=True, description="User ID who uploaded the document")