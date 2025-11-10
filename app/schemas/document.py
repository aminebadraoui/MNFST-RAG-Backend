"""
Document schemas
"""
from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID

from ..models.document import DocumentStatus


class DocumentBase(SQLModel):
    """Base document model"""
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


class DocumentRead(DocumentBase):
    """Document read model"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


class DocumentCreate(SQLModel):
    """Document creation model"""
    original_name: str = Field(description="Original filename")
    size: int = Field(description="File size in bytes")
    mime_type: str = Field(description="MIME type of the file")


class PresignedUrlResponse(SQLModel):
    """Presigned URL response model"""
    upload_url: str = Field(description="Pre-signed URL for direct upload to R2")
    file_key: str = Field(description="Unique file key in R2 bucket")
    document_id: UUID = Field(description="Unique document identifier")
    public_url: str = Field(description="Public URL for accessing the file")


class RegisterUploadRequest(SQLModel):
    """Register upload request model"""
    document_id: UUID = Field(description="Unique document identifier")
    file_name: str = Field(description="Original filename")
    file_key: str = Field(description="File key in R2 bucket")
    public_url: str = Field(description="Public URL for accessing the file")
    file_size: int = Field(description="File size in bytes")
    mime_type: str = Field(description="MIME type of the file")


class DocumentUploadStatus(SQLModel):
    """Document upload status model"""
    id: UUID = Field(description="Document ID")
    filename: str = Field(description="Document filename")
    status: DocumentStatus = Field(description="Document status")
    progress: int = Field(ge=0, le=100, description="Upload progress percentage")
    processed_at: Optional[datetime] = Field(
        default=None,
        description="Processing completion timestamp"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if processing failed"
    )


class UploadStatusResponse(SQLModel):
    """Upload status response model"""
    upload_id: UUID = Field(description="Upload identifier")
    status: str = Field(description="Overall upload status")
    documents: list[DocumentUploadStatus] = Field(description="Document statuses")


__all__ = [
    "DocumentRead",
    "DocumentCreate",
    "PresignedUrlResponse",
    "RegisterUploadRequest",
    "UploadStatusResponse",
    "DocumentUploadStatus"
]