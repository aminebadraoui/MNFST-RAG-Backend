"""
User schemas
"""
from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID

from ..models.user import UserRole


class UserBase(SQLModel):
    """Base user model"""
    email: str = Field(index=True, description="User's email address")
    name: str = Field(description="User's full name")
    role: UserRole = Field(description="User role in the system")
    tenant_id: Optional[UUID] = Field(
        default=None,
        foreign_key="tenants.id",
        index=True,
        description="Tenant ID (null for superadmin)"
    )
    last_login: Optional[datetime] = Field(
        default=None,
        description="Last login timestamp"
    )


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(description="User password")


class UserRead(UserBase):
    """User read model"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserUpdate(SQLModel):
    """User update model"""
    name: Optional[str] = None
    role: Optional[UserRole] = None


__all__ = ["UserCreate", "UserRead", "UserUpdate"]