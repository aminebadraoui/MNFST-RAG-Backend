"""
Social link model
"""
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


class SocialLink(SQLModel, BaseSQLModel, table=True):
    """Social link model with database fields"""
    
    __tablename__ = "social_links"
    
    url: str = Field(description="Social media URL")
    platform: SocialPlatform = Field(description="Social media platform type")
    tenant_id: UUID = Field(index=True, description="Tenant ID")