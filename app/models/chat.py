"""
Chat session and message models
"""
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from .base import BaseSQLModel


class MessageRole(str, Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"


class SessionBase(SQLModel):
    """Base chat session model"""
    title: str = Field(description="Session title")


class Session(SessionBase, BaseSQLModel, table=True):
    """Chat session model with database fields"""
    
    __tablename__ = "sessions"
    
    # Add user_id for multi-tenancy
    user_id: UUID = Field(index=True, description="User ID")
    
    # Relationships
    messages: list["Message"] = Relationship(back_populates="session")


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


class Message(MessageBase, BaseSQLModel, table=True):
    """Message model with database fields"""
    
    __tablename__ = "messages"
    
    # Add session_id for relationship
    session_id: UUID = Field(foreign_key="sessions.id", index=True, description="Session ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    
    # Relationships
    session: Session = Relationship(back_populates="messages")


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


# Import to avoid circular imports
if TYPE_CHECKING:
    pass