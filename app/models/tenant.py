"""
Tenant model
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

from .base import BaseSQLModel


class Tenant(BaseSQLModel, table=True):
    """Tenant model with database fields"""
    
    __tablename__ = "tenants"
    
    name: str = Field(description="Tenant display name")
    slug: str = Field(index=True, description="URL-safe tenant identifier")
    
    # Relationships
    users: list["User"] = Relationship(back_populates="tenant")


# Import User here to avoid circular imports
if TYPE_CHECKING:
    from .user import User