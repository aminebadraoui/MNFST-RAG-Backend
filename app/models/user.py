"""
User model
"""
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from .base import BaseSQLModel


class UserRole(str, Enum):
    """User role enumeration"""
    SUPERADMIN = "superadmin"
    TENANT_ADMIN = "tenant_admin"
    USER = "user"


class User(BaseSQLModel, table=True):
    """User model with database fields"""
    
    __tablename__ = "users"
    
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
    
    # Password hash
    password_hash: str = Field(description="Hashed password")
    
    # Relationships
    tenant: Optional["Tenant"] = Relationship(back_populates="users")
    sessions: list["Session"] = Relationship(back_populates="user")


# Import Tenant and Session here to avoid circular imports
if TYPE_CHECKING:
    from .tenant import Tenant
    from .chat import Session