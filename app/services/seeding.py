"""
Database seeding service for initial data
"""
import logging
from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlmodel import Session

from app.database import engine
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.services.password import PasswordService

logger = logging.getLogger(__name__)


class DatabaseSeedingError(Exception):
    """Database seeding error"""
    pass


class DatabaseSeeder:
    """Service for seeding initial database data"""
    
    def __init__(self):
        self.engine = engine
    
    def seed_superadmin_user(self, email: str = "admin@mnfst-rag.com", 
                          password: str = "admin123", 
                          name: str = "System Administrator") -> bool:
        """
        Create initial superadmin user if it doesn't exist
        
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
            logger.error(f"Failed to seed superadmin user: {e}")
            return False
    
    def seed_default_tenant(self, name: str = "Default Tenant", 
                          slug: str = "default") -> Optional[UUID]:
        """
        Create default tenant if it doesn't exist
        
        Args:
            name: Tenant display name
            slug: Tenant slug
            
        Returns:
            UUID: Tenant ID if created or exists, None if failed
        """
        try:
            with Session(self.engine) as session:
                # Check if tenant already exists
                existing_tenant = session.query(Tenant).where(
                    Tenant.slug == slug
                ).first()
                
                if existing_tenant:
                    logger.info(f"Default tenant '{slug}' already exists")
                    return existing_tenant.id
                
                # Create new tenant
                tenant = Tenant(
                    name=name,
                    slug=slug
                )
                
                session.add(tenant)
                session.commit()
                session.refresh(tenant)
                
                logger.info(f"Created default tenant: {name} ({slug})")
                return tenant.id
                
        except Exception as e:
            logger.error(f"Failed to seed default tenant: {e}")
            return None
    
    def seed_tenant_admin(self, tenant_id: UUID,
                        email: str = "tenant-admin@example.com",
                        password: str = "tenant123",
                        name: str = "Tenant Administrator") -> bool:
        """
        Create tenant admin user if it doesn't exist
        
        Args:
            tenant_id: Tenant ID
            email: Admin email
            password: Admin password
            name: Admin display name
            
        Returns:
            bool: True if user was created or already exists
        """
        try:
            with Session(self.engine) as session:
                # Check if admin already exists
                existing_user = session.query(User).where(
                    User.email == email,
                    User.role == UserRole.TENANT_ADMIN
                ).first()
                
                if existing_user:
                    logger.info(f"Tenant admin {email} already exists")
                    return True
                
                # Create new tenant admin
                admin = User(
                    email=email,
                    name=name,
                    password_hash=PasswordService.hash_password(password),
                    role=UserRole.TENANT_ADMIN,
                    tenant_id=tenant_id
                )
                
                session.add(admin)
                session.commit()
                session.refresh(admin)
                
                logger.info(f"Created tenant admin: {email} for tenant {tenant_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to seed tenant admin: {e}")
            return False
    
    def seed_initial_data(self) -> bool:
        """
        Seed all initial data in the correct order
        
        Returns:
            bool: True if all seeding was successful
        """
        try:
            logger.info("Starting database seeding...")
            
            # 1. Create superadmin user
            if not self.seed_superadmin_user():
                raise DatabaseSeedingError("Failed to seed superadmin user")
            
            # 2. Create default tenant
            tenant_id = self.seed_default_tenant()
            if not tenant_id:
                raise DatabaseSeedingError("Failed to seed default tenant")
            
            # 3. Create tenant admin
            if not self.seed_tenant_admin(tenant_id):
                raise DatabaseSeedingError("Failed to seed tenant admin")
            
            logger.info("Database seeding completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database seeding failed: {e}")
            return False
    
    def is_seeding_needed(self) -> bool:
        """
        Check if seeding is needed
        
        Returns:
            bool: True if seeding is needed
        """
        try:
            with Session(self.engine) as session:
                # Check if any users exist
                user_count = session.query(User).count()
                return user_count == 0
        except Exception as e:
            logger.error(f"Failed to check seeding status: {e}")
            return True  # Assume seeding is needed if we can't check
    
    def seed_if_needed(self) -> bool:
        """
        Seed data only if needed
        
        Returns:
            bool: True if seeding was successful or not needed
        """
        if not self.is_seeding_needed():
            logger.info("Database seeding not needed")
            return True
        
        return self.seed_initial_data()


# Global database seeder instance
database_seeder = DatabaseSeeder()


def seed_database_on_startup() -> bool:
    """
    Seed database during application startup
    
    Returns:
        bool: True if seeding was successful
    """
    try:
        return database_seeder.seed_if_needed()
    except Exception as e:
        logger.error(f"Database seeding failed: {e}")
        return False