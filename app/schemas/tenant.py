"""
Tenant schemas
"""
from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional, List
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
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Example Tenant",
                "slug": "example-tenant",
                "admin_email": "admin@example.com",
                "admin_name": "Admin User",
                "admin_password": "SecurePassword123"
            }
        }


class TenantRead(TenantBase):
    """Tenant read model"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_count: Optional[int] = Field(default=0, description="Number of users in tenant")
    document_count: Optional[int] = Field(default=0, description="Number of documents in tenant")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Example Tenant",
                "slug": "example-tenant",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "user_count": 5,
                "document_count": 10
            }
        }


class TenantUpdate(SQLModel):
    """Tenant update model"""
    name: Optional[str] = None
    slug: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Updated Tenant Name",
                "slug": "updated-tenant-slug"
            }
        }


class TenantReadWithAdmin(TenantRead):
    """Tenant read model with admin user info"""
    admin_user: Optional[dict] = Field(default=None, description="Admin user information")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Example Tenant",
                "slug": "example-tenant",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "user_count": 5,
                "document_count": 10,
                "admin_user": {
                    "id": "223e4567-e89b-12d3-a456-426614174000",
                    "email": "admin@example.com",
                    "name": "Admin User",
                    "role": "tenant_admin"
                }
            }
        }


__all__ = [
    "TenantCreate",
    "TenantRead",
    "TenantUpdate",
    "TenantReadWithAdmin"
]