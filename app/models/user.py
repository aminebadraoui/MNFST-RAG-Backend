"""
User model
"""
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from uuid import UUID

from .base import BaseSQLModel


class UserRole(str, Enum):
    """User role enumeration"""
    SUPERADMIN = "superadmin"
    TENANT_ADMIN = "tenant_admin"
    USER = "user"


class UserBase(SQLModel):
    """Base user model"""
    email: str = Field(index=True, description="User's email address")
    name: str = Field(description="User's full name")
    role: UserRole = Field(description="User role in the system")
    tenant_id: Optional[UUID] = Field(
        default=None,
        foreign_key="tenant.id",
        index=True,
        description="Tenant ID (null for superadmin)"
    )
    last_login: Optional[datetime] = Field(
        default=None,
        description="Last login timestamp"
    )


class User(UserBase, BaseSQLModel, table=True):
    """User model with database fields"""
    
    __tablename__ = "users"
    
    # Relationships
    tenant: Optional["Tenant"] = Relationship(back_populates="users")


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


# Import Tenant here to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .tenant import Tenant