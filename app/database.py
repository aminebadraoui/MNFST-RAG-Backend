"""
Database configuration and connection setup
"""
from sqlmodel import create_engine, SQLModel, Session
from typing import Generator

from app.config import settings

# Create database engine
engine = create_engine(settings.database_url, echo=settings.debug)


def create_db_and_tables() -> None:
    """Create database tables"""
    # TODO: Only create tables when database is available
    # For now, skip table creation to avoid connection errors
    # SQLModel.metadata.create_all(engine)
    pass


def get_session() -> Generator[Session, None, None]:
    """Get database session"""
    with Session(engine) as session:
        yield session