"""
Database configuration and connection setup
"""
import os
from sqlmodel import create_engine, SQLModel, Session
from typing import Generator
from sqlalchemy import event
from sqlalchemy.pool import QueuePool

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

# Get database URL directly from environment
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    raise ValueError("DATABASE_URL environment variable is not set")

# Connection pool settings
POOL_SIZE = int(os.environ.get('DB_POOL_SIZE', '5'))
MAX_OVERFLOW = int(os.environ.get('DB_MAX_OVERFLOW', '10'))
POOL_TIMEOUT = int(os.environ.get('DB_POOL_TIMEOUT', '30'))
POOL_RECYCLE = int(os.environ.get('DB_POOL_RECYCLE', '3600'))  # 1 hour

# Create database engine with proper connection pooling
engine = create_engine(
    db_url,
    echo=os.environ.get('DB_ECHO', 'false').lower() == 'true',
    poolclass=QueuePool,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=True,  # Validate connections before use
    connect_args={
        "application_name": "mnfst-rag-backend",
        "connect_timeout": 10,
    }
)

# Add connection event listeners for monitoring
@event.listens_for(engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    """Log when new connections are created"""
    print(f"New database connection created: {dbapi_connection.info}")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log when connections are checked out from pool"""
    print(f"Connection checked out from pool")

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log when connections are returned to pool"""
    print(f"Connection returned to pool")


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
    """Get database session with proper connection management"""
    session = Session(engine)
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_pool_status() -> dict:
    """Get current connection pool status"""
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "invalid": pool.invalid()
    }