"""
Database configuration and connection setup
"""
import os
from sqlmodel import create_engine, SQLModel, Session
from typing import Generator

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

# Get database URL directly from environment
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create database engine with environment URL
engine = create_engine(db_url, echo=True)


def create_db_and_tables() -> None:
    """Create database tables"""
    try:
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        # Log the error but don't fail startup
        # This allows the API to run even if database is not available
        print(f"Warning: Could not create database tables: {e}")
        print("API will continue running, but database operations may fail")


def get_session() -> Generator[Session, None, None]:
    """Get database session"""
    with Session(engine) as session:
        yield session