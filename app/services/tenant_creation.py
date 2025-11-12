"""
Tenant creation service for coordinating tenant and admin user creation
"""
from typing import Tuple
from sqlmodel import Session

from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.schemas.tenant import TenantCreate
from app.database import get_session
from app.services.tenant import TenantService
from app.services.user import UserService


class TenantCreationService:
    """Service for coordinating tenant creation with admin user"""
    
    @staticmethod
    def create_tenant_with_admin(tenant_data: TenantCreate) -> Tuple[Tenant, User]:
        """
        Create a new tenant with an admin user in a single transaction
        
        Args:
            tenant_data: Tenant creation data with admin user info
            
        Returns:
            Tuple of (created_tenant, created_admin_user)
            
        Raises:
            ValueError: If tenant slug already exists or admin user data is invalid
        """
        session = next(get_session())
        
        try:
            # Create tenant service without context manager (we'll handle transaction manually)
            tenant_service = TenantService(session)
            tenant = tenant_service.create_tenant(
                name=tenant_data.name,
                slug=tenant_data.slug
            )
            
            # Create admin user using the same session
            user_service = UserService(session)
            admin_user = user_service.create_user(
                email=tenant_data.admin_email,
                password=tenant_data.admin_password,
                name=tenant_data.admin_name,
                role=UserRole.TENANT_ADMIN,
                tenant_id=str(tenant.id)
            )
            
            # Commit the transaction first
            session.commit()
            
            # Then refresh to get latest data (after commit)
            session.refresh(tenant)
            session.refresh(admin_user)
            
            return tenant, admin_user
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


# Global tenant creation service instance
tenant_creation_service = TenantCreationService()