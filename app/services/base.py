"""
Base service class for common session management
"""
from abc import ABC
from typing import Optional, Generator
from sqlmodel import Session
from app.database import get_session


class BaseService(ABC):
    """Base service with session management"""
    
    def __init__(self, session: Optional[Session] = None):
        # Don't create a session in __init__ - it should be passed in
        # This prevents holding onto connections unnecessarily
        self._session = session
        self._owns_session = session is None
    
    @property
    def session(self) -> Session:
        """Get the current session, creating one if needed"""
        if self._session is None:
            raise RuntimeError("Session not initialized. Use with get_session() dependency or context manager.")
        return self._session
    
    def __enter__(self):
        if self._owns_session:
            self._session = next(get_session())
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._owns_session and self._session:
            if exc_type:
                self._session.rollback()
            else:
                self._session.commit()
            self._session.close()
            self._session = None


def with_session(service_class):
    """Decorator to inject session into service methods"""
    def wrapper(*args, **kwargs):
        # Get session from kwargs or create a new one
        session = kwargs.pop('session', None)
        if session is None:
            session = next(get_session())
            try:
                service = service_class(session)
                return service
            finally:
                session.close()
        else:
            return service_class(session)
    return wrapper