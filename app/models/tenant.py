"""
Tenant model
"""
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from .base import BaseSQLModel


class TenantBase(SQLModel):
    """Base tenant model"""
    name: str = Field(description="Tenant display name")
    slug: str = Field(index=True, description="URL-safe tenant identifier")


class Tenant(TenantBase, BaseSQLModel, table=True):
    """Tenant model with database fields"""
    
    __tablename__ = "tenants"
    
    # Relationships
    users: list["User"] = Relationship(back_populates="tenant")


class TenantCreate(TenantBase):
    """Tenant creation model"""
    admin_user: "UserCreate" = Field(description="Admin user for tenant")


class TenantRead(TenantBase):
    """Tenant read model"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_count: Optional[int] = Field(default=0, description="Number of users in tenant")
    document_count: Optional[int] = Field(default=0, description="Number of documents in tenant")


class TenantUpdate(SQLModel):
    """Tenant update model"""
    name: Optional[str] = None
    slug: Optional[str] = None


# Import User here to avoid circular imports
if TYPE_CHECKING:
    from .user import User, UserCreate