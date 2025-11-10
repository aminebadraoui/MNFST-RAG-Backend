"""
Chat schemas
"""
from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID

from ..models.chat import MessageRole


class SessionBase(SQLModel):
    """Base chat session model"""
    title: str = Field(description="Session title")


class SessionRead(SessionBase):
    """Chat session read model"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: UUID


class SessionCreate(SessionBase):
    """Chat session creation model"""
    pass


class MessageBase(SQLModel):
    """Base message model"""
    content: str = Field(description="Message content")
    role: MessageRole = Field(description="Message role in conversation")


class MessageRead(MessageBase):
    """Message read model"""
    id: UUID
    session_id: UUID
    timestamp: datetime


class MessageCreate(MessageBase):
    """Message creation model"""
    session_id: UUID = Field(description="Session ID")
    stream: Optional[bool] = Field(default=False, description="Whether to request streaming response")


class SendMessageRequest(SQLModel):
    """Send message request model"""
    content: str = Field(description="Message content")
    role: str = Field(default="user", description="Message role (always 'user' for sent messages)")
    stream: Optional[bool] = Field(default=False, description="Whether to request streaming response")


class StreamChunk(SQLModel):
    """Stream chunk model for streaming responses"""
    type: str = Field(description="Stream event type")
    message_id: Optional[UUID] = Field(default=None, description="Message ID (for start/end events)")
    content: Optional[str] = Field(default=None, description="Token content (for token events)")
    complete: Optional[bool] = Field(default=False, description="Whether streaming is complete")
    error: Optional[str] = Field(default=None, description="Error message (for error events)")


__all__ = [
    "SessionRead",
    "SessionCreate",
    "MessageRead",
    "MessageCreate",
    "SendMessageRequest",
    "StreamChunk"
]