"""
Tenant schemas
"""
from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID


class TenantBase(SQLModel):
    """Base tenant model"""
    name: str = Field(description="Tenant display name")
    slug: str = Field(index=True, description="URL-safe tenant identifier")


class TenantCreate(TenantBase):
    """Tenant creation model"""
    admin_email: str = Field(description="Admin user email for tenant")
    admin_name: str = Field(description="Admin user name for tenant")
    admin_password: str = Field(description="Admin user password for tenant")


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


__all__ = ["TenantCreate", "TenantRead", "TenantUpdate"]