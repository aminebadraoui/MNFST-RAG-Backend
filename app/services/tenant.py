"""
Tenant service for managing tenant operations
"""
from typing import Optional, Tuple, List
from sqlmodel import Session, select, func, delete
from uuid import UUID

from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.models.document import Document
from app.models.social import SocialLink
from app.schemas.tenant import TenantCreate, TenantUpdate
from app.database import get_session
from app.services.auth import auth_service
from app.exceptions.auth import AuthenticationError


class TenantService:
    """Service for tenant operations"""
    
    @staticmethod
    def create_tenant_with_admin(
        tenant_data: TenantCreate
    ) -> Tuple[Tenant, User]:
        """
        Create a new tenant with an admin user
        
        Args:
            tenant_data: Tenant creation data with admin user info
            
        Returns:
            Tuple of (created_tenant, created_admin_user)
            
        Raises:
            ValueError: If tenant slug already exists or admin user data is invalid
        """
        session = next(get_session())
        
        try:
            # Check if tenant slug already exists
            statement = select(Tenant).where(Tenant.slug == tenant_data.slug)
            existing_tenant = session.exec(statement).first()
            if existing_tenant:
                raise ValueError(f"Tenant with slug '{tenant_data.slug}' already exists")
            
            # Check if admin email already exists
            statement = select(User).where(User.email == tenant_data.admin_email)
            existing_user = session.exec(statement).first()
            if existing_user:
                raise ValueError(f"User with email '{tenant_data.admin_email}' already exists")
            
            # Create tenant
            tenant = Tenant(
                name=tenant_data.name,
                slug=tenant_data.slug
            )
            session.add(tenant)
            session.flush()  # Get the tenant ID without committing
            
            # Create admin user
            admin_user = auth_service.create_user_with_password(
                email=tenant_data.admin_email,
                password=tenant_data.admin_password,
                name=tenant_data.admin_name,
                role=UserRole.TENANT_ADMIN,
                tenant_id=str(tenant.id)
            )
            
            session.commit()
            session.refresh(tenant)
            session.refresh(admin_user)
            
            return tenant, admin_user
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_all_tenants() -> List[Tenant]:
        """
        Get all tenants
        
        Returns:
            List of all tenants
        """
        session = next(get_session())
        
        try:
            statement = select(Tenant)
            tenants = session.exec(statement).all()
            return list(tenants)
            
        finally:
            session.close()
    
    @staticmethod
    def get_tenant_by_id(tenant_id: str) -> Optional[Tenant]:
        """
        Get tenant by ID
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Tenant object if found, None otherwise
        """
        session = next(get_session())
        
        try:
            statement = select(Tenant).where(Tenant.id == tenant_id)
            tenant = session.exec(statement).first()
            return tenant
            
        finally:
            session.close()
    
    @staticmethod
    def update_tenant(tenant_id: str, tenant_data: TenantUpdate) -> Optional[Tenant]:
        """
        Update tenant information
        
        Args:
            tenant_id: Tenant ID
            tenant_data: Tenant update data
            
        Returns:
            Updated tenant object if found, None otherwise
            
        Raises:
            ValueError: If new slug already exists
        """
        session = next(get_session())
        
        try:
            # Get existing tenant
            statement = select(Tenant).where(Tenant.id == tenant_id)
            tenant = session.exec(statement).first()
            if not tenant:
                return None
            
            # Check if new slug already exists (if slug is being updated)
            if tenant_data.slug and tenant_data.slug != tenant.slug:
                statement = select(Tenant).where(Tenant.slug == tenant_data.slug)
                existing_tenant = session.exec(statement).first()
                if existing_tenant:
                    raise ValueError(f"Tenant with slug '{tenant_data.slug}' already exists")
            
            # Update tenant fields
            if tenant_data.name is not None:
                tenant.name = tenant_data.name
            if tenant_data.slug is not None:
                tenant.slug = tenant_data.slug
            
            session.add(tenant)
            session.commit()
            session.refresh(tenant)
            
            return tenant
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def delete_tenant_cascade(tenant_id: str) -> bool:
        """
        Delete tenant and all associated data (users, documents, social links)
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            True if tenant was deleted, False if tenant was not found
        """
        session = next(get_session())
        
        try:
            # Check if tenant exists
            statement = select(Tenant).where(Tenant.id == tenant_id)
            tenant = session.exec(statement).first()
            if not tenant:
                return False
            
            # Delete social links for tenant
            statement = delete(SocialLink).where(SocialLink.tenant_id == tenant_id)
            session.exec(statement)
            
            # Delete documents for tenant
            statement = delete(Document).where(Document.tenant_id == tenant_id)
            session.exec(statement)
            
            # Delete users for tenant
            statement = delete(User).where(User.tenant_id == tenant_id)
            session.exec(statement)
            
            # Delete tenant
            statement = delete(Tenant).where(Tenant.id == tenant_id)
            session.exec(statement)
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_tenant_stats(tenant_id: str) -> dict:
        """
        Get tenant statistics (user count, document count)
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Dictionary with tenant statistics
        """
        session = next(get_session())
        
        try:
            # Get user count
            user_count_statement = select(func.count(User.id)).where(User.tenant_id == tenant_id)
            user_count = session.exec(user_count_statement).one()
            
            # Get document count
            doc_count_statement = select(func.count(Document.id)).where(Document.tenant_id == tenant_id)
            document_count = session.exec(doc_count_statement).one()
            
            return {
                "user_count": user_count,
                "document_count": document_count
            }
            
        finally:
            session.close()


# Global tenant service instance
tenant_service = TenantService()