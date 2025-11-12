"""
Base service class for common session management
"""
from abc import ABC
from typing import Optional
from sqlmodel import Session
from app.database import get_session


class BaseService(ABC):
    """Base service with session management"""
    
    def __init__(self, session: Optional[Session] = None):
        self.session = session or next(get_session())
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()