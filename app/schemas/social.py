"""
Social link schemas
"""
from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID

from ..models.social import SocialPlatform


class SocialLinkBase(SQLModel):
    """Base social link model"""
    url: str = Field(description="Social media URL")
    platform: SocialPlatform = Field(description="Social media platform type")


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


__all__ = ["SocialLinkRead", "SocialLinkCreate", "AddLinkRequest"]