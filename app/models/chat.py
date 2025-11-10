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


class Session(SQLModel, BaseSQLModel, table=True):
    """Chat session model with database fields"""
    
    __tablename__ = "sessions"
    
    title: str = Field(description="Session title")
    user_id: UUID = Field(index=True, description="User ID")
    
    # Relationships
    messages: list["Message"] = Relationship(back_populates="session")


class Message(SQLModel, BaseSQLModel, table=True):
    """Message model with database fields"""
    
    __tablename__ = "messages"
    
    content: str = Field(description="Message content")
    role: MessageRole = Field(description="Message role in conversation")
    session_id: UUID = Field(foreign_key="sessions.id", index=True, description="Session ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    
    # Relationships
    session: Session = Relationship(back_populates="messages")


# Import to avoid circular imports
if TYPE_CHECKING:
    pass