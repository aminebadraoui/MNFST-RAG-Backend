"""
Social link model
"""
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID

from .base import BaseSQLModel


class SocialPlatform(str, Enum):
    """Social media platform enumeration"""
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    OTHER = "other"


class SocialLinkBase(SQLModel):
    """Base social link model"""
    url: str = Field(description="Social media URL")
    platform: SocialPlatform = Field(description="Social media platform type")


class SocialLink(SocialLinkBase, BaseSQLModel, table=True):
    """Social link model with database fields"""
    
    __tablename__ = "social_links"
    
    # Add tenant_id for multi-tenancy
    tenant_id: UUID = Field(index=True, description="Tenant ID")


class SocialLinkRead(SocialLinkBase):
    """Social link read model"""
    id: UUID
    added_at: datetime
    tenant_id: UUID


class SocialLinkCreate(SocialLinkBase):
    """Social link creation model"""
    pass


class AddLinkRequest(SQLModel):
    """Add link request model"""
    url: str = Field(description="Social media URL")