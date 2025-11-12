"""
Tenant service for managing tenant operations
"""
from typing import Optional, List
from sqlmodel import Session, select, func, delete
from uuid import UUID

from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.models.document import Document
from app.models.social import SocialLink
from app.schemas.tenant import TenantCreate, TenantUpdate
from app.database import get_session
from app.services.base import BaseService


class TenantService(BaseService):
    """Service for tenant operations"""
    
    def create_tenant(self, name: str, slug: str) -> Tenant:
        """
        Create a new tenant (without transaction management)
        
        Args:
            name: Tenant name
            slug: Tenant slug
            
        Returns:
            Created tenant object
            
        Raises:
            ValueError: If tenant slug already exists
        """
        # Check if tenant slug already exists
        statement = select(Tenant).where(Tenant.slug == slug)
        existing_tenant = self.session.exec(statement).first()
        if existing_tenant:
            raise ValueError(f"Tenant with slug '{slug}' already exists")
        
        # Create tenant
        tenant = Tenant(name=name, slug=slug)
        self.session.add(tenant)
        self.session.flush()  # Get ID without committing
        return tenant
    
    def get_all_tenants(self) -> List[Tenant]:
        """
        Get all tenants
        
        Returns:
            List of all tenants
        """
        statement = select(Tenant)
        tenants = self.session.exec(statement).all()
        return list(tenants)
    
    @staticmethod
    def get_all_tenants_static() -> List[Tenant]:
        """
        Get all tenants (static method for backward compatibility)
        
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
    
    def get_tenant_by_id(self, tenant_id: str) -> Optional[Tenant]:
        """
        Get tenant by ID
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Tenant object if found, None otherwise
        """
        statement = select(Tenant).where(Tenant.id == tenant_id)
        tenant = self.session.exec(statement).first()
        return tenant
    
    @staticmethod
    def get_tenant_by_id_static(tenant_id: str) -> Optional[Tenant]:
        """
        Get tenant by ID (static method for backward compatibility)
        
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
    
    def update_tenant(self, tenant_id: str, tenant_data: TenantUpdate) -> Optional[Tenant]:
        """
        Update tenant information (without transaction management)
        
        Args:
            tenant_id: Tenant ID
            tenant_data: Tenant update data
            
        Returns:
            Updated tenant object if found, None otherwise
            
        Raises:
            ValueError: If new slug already exists
        """
        # Get existing tenant
        statement = select(Tenant).where(Tenant.id == tenant_id)
        tenant = self.session.exec(statement).first()
        if not tenant:
            return None
        
        # Check if new slug already exists (if slug is being updated)
        if tenant_data.slug and tenant_data.slug != tenant.slug:
            statement = select(Tenant).where(Tenant.slug == tenant_data.slug)
            existing_tenant = self.session.exec(statement).first()
            if existing_tenant:
                raise ValueError(f"Tenant with slug '{tenant_data.slug}' already exists")
        
        # Update tenant fields
        if tenant_data.name is not None:
            tenant.name = tenant_data.name
        if tenant_data.slug is not None:
            tenant.slug = tenant_data.slug
        
        self.session.add(tenant)
        self.session.flush()  # Get updated data without committing
        return tenant
    
    def delete_tenant_cascade(self, tenant_id: str) -> bool:
        """
        Delete tenant and all associated data (users, documents, social links)
        (without transaction management)
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            True if tenant was deleted, False if tenant was not found
        """
        # Check if tenant exists
        statement = select(Tenant).where(Tenant.id == tenant_id)
        tenant = self.session.exec(statement).first()
        if not tenant:
            return False
        
        # Delete social links for tenant
        statement = delete(SocialLink).where(SocialLink.tenant_id == tenant_id)
        self.session.exec(statement)
        
        # Delete documents for tenant
        statement = delete(Document).where(Document.tenant_id == tenant_id)
        self.session.exec(statement)
        
        # Delete users for tenant
        statement = delete(User).where(User.tenant_id == tenant_id)
        self.session.exec(statement)
        
        # Delete tenant
        statement = delete(Tenant).where(Tenant.id == tenant_id)
        self.session.exec(statement)
        
        return True
    
    @staticmethod
    def delete_tenant_cascade_static(tenant_id: str) -> bool:
        """
        Delete tenant and all associated data (users, documents, social links)
        (static method for backward compatibility)
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            True if tenant was deleted, False if tenant was not found
        """
        session = next(get_session())
        try:
            ts = TenantService(session)
            deleted = ts.delete_tenant_cascade(tenant_id)
            if deleted:
                session.commit()
            return deleted
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_tenant_stats(self, tenant_id: str) -> dict:
        """
        Get tenant statistics (user count, document count)
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Dictionary with tenant statistics
        """
        # Get user count
        user_count_statement = select(func.count(User.id)).where(User.tenant_id == tenant_id)
        user_count = self.session.exec(user_count_statement).one()
        
        # Get document count
        doc_count_statement = select(func.count(Document.id)).where(Document.tenant_id == tenant_id)
        document_count = self.session.exec(doc_count_statement).one()
        
        return {
            "user_count": user_count,
            "document_count": document_count
        }
    
    @staticmethod
    def get_tenant_stats_static(tenant_id: str) -> dict:
        """
        Get tenant statistics (user count, document count)
        (static method for backward compatibility)
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Dictionary with tenant statistics
        """
        session = next(get_session())
        try:
            ts = TenantService(session)
            return ts.get_tenant_stats(tenant_id)
        finally:
            session.close()


# Global tenant service instance (for backward compatibility)
tenant_service = TenantService()

# Override methods to use static versions for backward compatibility
tenant_service.get_all_tenants = TenantService.get_all_tenants_static
tenant_service.get_tenant_by_id = TenantService.get_tenant_by_id_static
tenant_service.get_tenant_stats = TenantService.get_tenant_stats_static
tenant_service.delete_tenant_cascade = TenantService.delete_tenant_cascade_static