"""
Chat schemas
"""
from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional, List
from uuid import UUID


class ChatBase(SQLModel):
    """Base chat model"""
    name: str = Field(description="Chat display name")
    system_prompt: Optional[str] = Field(default=None, description="System prompt for AI assistant")


class ChatCreate(ChatBase):
    """Chat creation model"""
    pass


class ChatRead(ChatBase):
    """Chat read model"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    tenant_id: UUID
    session_count: Optional[int] = Field(default=0, description="Number of sessions in chat")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Customer Support Bot",
                "system_prompt": "You are a helpful customer support assistant...",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "tenant_id": "223e4567-e89b-12d3-a456-426614174001",
                "session_count": 5
            }
        }


class ChatUpdate(SQLModel):
    """Chat update model"""
    name: Optional[str] = None
    system_prompt: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Updated Chat Name",
                "system_prompt": "You are an updated helpful assistant..."
            }
        }


class SessionBase(SQLModel):
    """Base chat session model"""
    title: str = Field(description="Session title")


class SessionRead(SessionBase):
    """Chat session read model"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: UUID
    chat_id: UUID
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Customer Support Conversation",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "user_id": "223e4567-e89b-12d3-a456-426614174001",
                "chat_id": "323e4567-e89b-12d3-a456-426614174002"
            }
        }


class SessionCreate(SessionBase):
    """Chat session creation model"""
    chat_id: UUID = Field(description="Chat ID")


class MessageBase(SQLModel):
    """Base message model"""
    content: str = Field(description="Message content")
    role: str = Field(description="Message role in conversation")


class MessageRead(MessageBase):
    """Message read model"""
    id: UUID
    session_id: UUID
    timestamp: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "content": "Hello, how can I help you?",
                "role": "assistant",
                "session_id": "223e4567-e89b-12d3-a456-426614174001",
                "timestamp": "2023-01-01T00:00:00Z"
            }
        }


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
    "ChatCreate",
    "ChatRead",
    "ChatUpdate",
    "SessionRead",
    "SessionCreate",
    "MessageRead",
    "MessageCreate",
    "SendMessageRequest",
    "StreamChunk"
]