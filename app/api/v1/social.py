"""
Social links endpoints
"""
from fastapi import APIRouter, HTTPException, status
from typing import Any, List

from app.schemas.social import SocialLinkRead, SocialLinkCreate, AddLinkRequest

router = APIRouter()


@router.get("/", response_model=List[SocialLinkRead])
async def get_social_links() -> Any:
    """
    Get social links
    Retrieve all social links for current tenant (tenant admin only)
    """
    # TODO: Implement actual social links retrieval logic
    # For now, return empty list
    return []


@router.post("/", response_model=SocialLinkRead, status_code=status.HTTP_201_CREATED)
async def add_social_link(link_data: AddLinkRequest) -> Any:
    """
    Add social link
    Add a new social media link for current tenant (tenant admin only)
    """
    # TODO: Implement actual social link creation logic
    # For now, return mock data
    from uuid import uuid4
    from datetime import datetime
    
    return SocialLinkRead(
        id=uuid4(),
        url=link_data.url,
        platform="other",  # TODO: Detect platform from URL
        added_at=datetime.utcnow(),
        tenant_id="mock-tenant-id"
    )


@router.delete("/{link_id}")
async def delete_social_link(link_id: str) -> Any:
    """
    Delete social link
    Remove a social media link from current tenant (tenant admin only)
    """
    # TODO: Implement actual social link deletion logic
    # For now, just return success
    from fastapi import Response
    return Response(status_code=status.HTTP_204_NO_CONTENT)