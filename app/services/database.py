"""
Database initialization and migration service
"""
import os
import time
import logging
from typing import Optional
from contextlib import contextmanager
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory

from app.database import engine
from app.config import settings

logger = logging.getLogger(__name__)


class DatabaseInitializationError(Exception):
    """Database initialization error"""
    pass


class DatabaseService:
    """Service for database initialization and migration management"""
    
    def __init__(self):
        # Load environment variables first
        from dotenv import load_dotenv
        load_dotenv()
        
        # Get database URL directly from environment
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        logger.info(f"Database URL from env: {db_url.split('@')[0] if '@' in db_url else 'URL not set'}")
        
        # Create engine with the correct URL
        from sqlalchemy import create_engine
        self.engine = create_engine(db_url)
        
        self.alembic_cfg = Config("alembic.ini")
        self.alembic_cfg.set_main_option("sqlalchemy.url", db_url)
        
    def is_database_initialized(self) -> bool:
        """Check if database is already initialized with tables"""
        try:
            with self.engine.connect() as connection:
                # Check if alembic_version table exists
                result = connection.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'alembic_version'
                    );
                """))
                return result.scalar()
        except (SQLAlchemyError, OperationalError) as e:
            logger.warning(f"Failed to check database initialization status: {e}")
            return False
    
    def get_current_migration_version(self) -> Optional[str]:
        """Get current migration version from database"""
        try:
            with self.engine.connect() as connection:
                context = MigrationContext.configure(connection)
                return context.get_current_revision()
        except (SQLAlchemyError, OperationalError):
            return None
    
    def get_latest_migration_version(self) -> Optional[str]:
        """Get latest available migration version"""
        try:
            script_dir = ScriptDirectory.from_config(self.alembic_cfg)
            return script_dir.get_current_head()
        except Exception as e:
            logger.error(f"Failed to get latest migration version: {e}")
            return None
    
    def needs_migration(self) -> bool:
        """Check if database needs migration"""
        current = self.get_current_migration_version()
        latest = self.get_latest_migration_version()
        return current != latest
    
    def wait_for_database(self, max_retries: int = 5, retry_interval: float = 2.0) -> bool:
        """Wait for database to be available"""
        for attempt in range(max_retries):
            try:
                with self.engine.connect() as connection:
                    connection.execute(text("SELECT 1"))
                logger.info("Database connection successful")
                return True
            except OperationalError as e:
                logger.warning(f"Database connection attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_interval)
                else:
                    logger.error("Max database connection retries exceeded")
                    logger.error("APPLICATION WILL CONTINUE WITHOUT DATABASE CONNECTION")
                    logger.error("Please check your Supabase dashboard for the correct connection string")
                    logger.error("Update your .env file with the correct DATABASE_URL")
                    return False
        return False
    
    def create_database_lock(self) -> bool:
        """Create a database lock to prevent concurrent initializations"""
        try:
            with self.engine.connect() as connection:
                # Try to acquire an advisory lock
                result = connection.execute(text("SELECT pg_try_advisory_lock(123456789)"))
                lock_acquired = result.scalar()
                if lock_acquired:
                    logger.info("Database initialization lock acquired")
                else:
                    logger.warning("Database initialization already in progress")
                return lock_acquired
        except (SQLAlchemyError, OperationalError) as e:
            logger.error(f"Failed to create database lock: {e}")
            return False
    
    def release_database_lock(self) -> None:
        """Release the database lock"""
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT pg_advisory_unlock(123456789)"))
                logger.info("Database initialization lock released")
        except (SQLAlchemyError, OperationalError) as e:
            logger.error(f"Failed to release database lock: {e}")
    
    def run_migrations(self) -> bool:
        """Run database migrations using Alembic"""
        try:
            logger.info("Running database migrations...")
            command.upgrade(self.alembic_cfg, "head")
            logger.info("Database migrations completed successfully")
            return True
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def initialize_database(self, force: bool = False) -> bool:
        """
        Initialize database with migrations in an idempotent way
        
        Args:
            force: Force re-initialization even if already initialized
            
        Returns:
            bool: True if initialization was successful
        """
        # Wait for database to be available
        if not self.wait_for_database():
            raise DatabaseInitializationError("Database is not available")
        
        # Check if already initialized
        if not force and self.is_database_initialized():
            if self.needs_migration():
                logger.info("Database initialized but needs migration")
                return self.run_migrations()
            else:
                logger.info("Database already initialized and up to date")
                return True
        
        # Acquire lock to prevent concurrent initializations
        if not self.create_database_lock():
            logger.info("Another process is initializing the database")
            # Wait a bit and check if initialization completed
            time.sleep(5)
            return self.is_database_initialized()
        
        try:
            # Run migrations
            success = self.run_migrations()
            if success:
                logger.info("Database initialization completed successfully")
            return success
        finally:
            # Always release the lock
            self.release_database_lock()
    
    def get_migration_status(self) -> dict:
        """Get current migration status"""
        current = self.get_current_migration_version()
        latest = self.get_latest_migration_version()
        
        return {
            "current_revision": current,
            "latest_revision": latest,
            "needs_migration": current != latest,
            "database_available": self._check_database_availability()
        }
    
    def _check_database_availability(self) -> bool:
        """Check if database is available"""
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except (SQLAlchemyError, OperationalError):
            return False


# Global database service instance
database_service = DatabaseService()


@contextmanager
def database_lock():
    """Context manager for database operations requiring lock"""
    if database_service.create_database_lock():
        try:
            yield
        finally:
            database_service.release_database_lock()
    else:
        raise DatabaseInitializationError("Could not acquire database lock")


def initialize_database_on_startup(force: bool = False) -> bool:
    """
    Initialize database during application startup
    
    Args:
        force: Force re-initialization
        
    Returns:
        bool: True if initialization was successful
    """
    try:
        return database_service.initialize_database(force=force)
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False