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


class Chat(BaseSQLModel, table=True):
    """Chat model with database fields"""
    
    __tablename__ = "chats"
    
    name: str = Field(description="Chat display name")
    system_prompt: Optional[str] = Field(default=None, description="System prompt for AI assistant")
    tenant_id: UUID = Field(foreign_key="tenants.id", index=True, description="Tenant ID")
    
    # Relationships
    tenant: "Tenant" = Relationship(back_populates="chats")
    sessions: list["Session"] = Relationship(back_populates="chat")


class Session(BaseSQLModel, table=True):
    """Chat session model with database fields"""
    
    __tablename__ = "sessions"
    
    title: str = Field(description="Session title")
    user_id: UUID = Field(foreign_key="users.id", index=True, description="User ID")
    chat_id: UUID = Field(foreign_key="chats.id", index=True, description="Chat ID")
    
    # Relationships
    user: "User" = Relationship(back_populates="sessions")
    chat: "Chat" = Relationship(back_populates="sessions")
    messages: list["Message"] = Relationship(back_populates="session")


class Message(BaseSQLModel, table=True):
    """Message model with database fields"""
    
    __tablename__ = "messages"
    
    content: str = Field(description="Message content")
    role: MessageRole = Field(description="Message role in conversation")
    session_id: UUID = Field(foreign_key="sessions.id", index=True, description="Session ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    
    # Relationships
    session: "Session" = Relationship(back_populates="messages")


# Import to avoid circular imports
if TYPE_CHECKING:
    from .tenant import Tenant
    from .user import User