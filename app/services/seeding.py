"""
Database seeding service for creating superadmin users
"""
import logging
from sqlmodel import Session

from app.database import engine
from app.models.user import User, UserRole
from app.services.password import PasswordService

logger = logging.getLogger(__name__)


class DatabaseSeeder:
    """Service for creating superadmin users"""
    
    def __init__(self):
        self.engine = engine
    
    def create_superadmin(self, email: str, password: str, name: str = "System Administrator") -> bool:
        """
        Create a superadmin user if it doesn't exist
        
        Args:
            email: Superadmin email
            password: Superadmin password
            name: Superadmin display name
            
        Returns:
            bool: True if user was created or already exists
        """
        try:
            with Session(self.engine) as session:
                # Check if superadmin already exists
                existing_user = session.query(User).where(
                    User.email == email,
                    User.role == UserRole.SUPERADMIN
                ).first()
                
                if existing_user:
                    logger.info(f"Superadmin user {email} already exists")
                    return True
                
                # Create new superadmin user
                superadmin = User(
                    email=email,
                    name=name,
                    password_hash=PasswordService.hash_password(password),
                    role=UserRole.SUPERADMIN,
                    tenant_id=None  # Superadmin has no tenant
                )
                
                session.add(superadmin)
                session.commit()
                session.refresh(superadmin)
                
                logger.info(f"Created superadmin user: {email}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create superadmin user: {e}")
            return False


# Global database seeder instance
database_seeder = DatabaseSeeder()