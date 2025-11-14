"""
Chat service
"""
from typing import Optional, Dict, Any
from uuid import UUID
from sqlmodel import select, func, desc, asc

from app.models.chat import Chat, Session, Message
from app.models.user import User
from app.services.base import BaseService
from app.database import get_session


class ChatService(BaseService):
    """Service for managing chats and sessions"""
    
    def get_tenant_chats(self, tenant_id: str) -> list[Chat]:
        """Get all chats for a tenant"""
        try:
            statement = select(Chat).where(Chat.tenant_id == UUID(tenant_id))
            return self.session.exec(statement).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_chat_by_id(self, chat_id: str) -> Optional[Chat]:
        """Get chat by ID"""
        try:
            statement = select(Chat).where(Chat.id == UUID(chat_id))
            return self.session.exec(statement).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def create_chat(self, tenant_id: str, name: str, system_prompt: Optional[str] = None) -> Chat:
        """Create a new chat"""
        try:
            chat = Chat(
                name=name,
                system_prompt=system_prompt,
                tenant_id=UUID(tenant_id)
            )
            self.session.add(chat)
            self.session.commit()
            self.session.refresh(chat)
            return chat
        except Exception as e:
            self.session.rollback()
            raise e
    
    def update_chat(self, chat_id: str, chat_data: Dict[str, Any]) -> Optional[Chat]:
        """Update chat"""
        try:
            statement = select(Chat).where(Chat.id == UUID(chat_id))
            chat = self.session.exec(statement).first()
            
            if not chat:
                return None
            
            # Update fields if provided
            if "name" in chat_data and chat_data["name"]:
                chat.name = chat_data["name"]
            
            if "system_prompt" in chat_data:
                # Convert empty string to None to maintain consistency
                system_prompt = chat_data["system_prompt"]
                chat.system_prompt = system_prompt if system_prompt else None
            
            self.session.commit()
            self.session.refresh(chat)
            return chat
        except Exception as e:
            self.session.rollback()
            raise e
    
    def delete_chat_cascade(self, chat_id: str) -> bool:
        """Delete chat and all associated sessions and messages"""
        try:
            statement = select(Chat).where(Chat.id == UUID(chat_id))
            chat = self.session.exec(statement).first()
            
            if not chat:
                return False
            
            self.session.delete(chat)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_chat_stats(self, chat_id: str) -> Dict[str, int]:
        """Get statistics for a chat"""
        # Count sessions
        session_count = self.session.exec(
            select(func.count(Session.id)).where(Session.chat_id == UUID(chat_id))
        ).one() or 0
        
        return {
            "session_count": session_count
        }
    
    def get_chat_sessions(self, chat_id: str, user_id: Optional[str] = None) -> list[Session]:
        """Get sessions for a chat, optionally filtered by user"""
        statement = select(Session).where(Session.chat_id == UUID(chat_id))
        
        if user_id:
            statement = statement.where(Session.user_id == UUID(user_id))
        
        statement = statement.order_by(desc(Session.updated_at))
        return self.session.exec(statement).all()
    
    def create_session(self, chat_id: str, user_id: str, title: str) -> Session:
        """Create a new session"""
        session = Session(
            title=title,
            chat_id=UUID(chat_id),
            user_id=UUID(user_id)
        )
        self.session.add(session)
        self.session.commit()
        self.session.refresh(session)
        return session
    
    def get_session_by_id(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        statement = select(Session).where(Session.id == UUID(session_id))
        return self.session.exec(statement).first()
    
    def delete_session_cascade(self, session_id: str) -> bool:
        """Delete session and all associated messages"""
        statement = select(Session).where(Session.id == UUID(session_id))
        session = self.session.exec(statement).first()
        
        if not session:
            return False
        
        self.session.delete(session)
        self.session.commit()
        return True
    
    def get_session_messages(self, session_id: str) -> list[Message]:
        """Get messages for a session"""
        statement = select(Message).where(
            Message.session_id == UUID(session_id)
        ).order_by(asc(Message.timestamp))
        return self.session.exec(statement).all()
    
    def create_message(self, session_id: str, content: str, role: str) -> Message:
        """Create a new message"""
        message = Message(
            content=content,
            role=role,
            session_id=UUID(session_id)
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message


# Create singleton instance
def get_chat_service() -> ChatService:
    """Get chat service instance"""
    return ChatService(next(get_session()))


# Create a global instance to be used across the application
chat_service = get_chat_service()