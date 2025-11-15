"""
Chat management endpoints
"""
from fastapi import APIRouter, HTTPException, status, Query, Depends, Response
from typing import Any, List
from sqlmodel import Session

from app.schemas.chat import (
    ChatRead,
    ChatCreate,
    ChatUpdate
)
from app.schemas.response import DataResponse
from app.services.chat import ChatService, get_chat_service
from app.database import get_session
from app.dependencies.auth import get_current_user, require_tenant_admin
from app.models.user import User

router = APIRouter()


@router.get("", response_model=DataResponse[List[ChatRead]])
async def get_chats(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Any:
    """
    Get chats
    Retrieve all chats for current user's tenant
    """
    try:
        chat_service_instance = get_chat_service(session)
        chats = chat_service_instance.get_tenant_chats(str(current_user.tenant_id))
        
        # Get stats for each chat
        chats_with_stats = []
        for chat in chats:
            stats = chat_service_instance.get_chat_stats(str(chat.id))
            chat_read = ChatRead(
                id=chat.id,
                name=chat.name,
                system_prompt=chat.system_prompt,
                created_at=chat.created_at,
                updated_at=chat.updated_at,
                tenant_id=chat.tenant_id,
                session_count=stats["session_count"]
            )
            chats_with_stats.append(chat_read)
        
        return DataResponse(
            data=chats_with_stats,
            message="Chats retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chats: {str(e)}"
        )


@router.post("", response_model=DataResponse[ChatRead], status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_data: ChatCreate,
    current_user: User = Depends(require_tenant_admin)
) -> Any:
    """
    Create chat
    Create a new chat for the tenant (tenant admin only)
    """
    try:
        chat = chat_service_instance.create_chat(
            tenant_id=str(current_user.tenant_id),
            name=chat_data.name,
            system_prompt=chat_data.system_prompt
        )
        
        chat_response = ChatRead(
            id=chat.id,
            name=chat.name,
            system_prompt=chat.system_prompt,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            tenant_id=chat.tenant_id,
            session_count=0
        )
        
        return DataResponse(
            data=chat_response,
            message="Chat created successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chat: {str(e)}"
        )


@router.get("/{chatId}", response_model=DataResponse[ChatRead])
async def get_chat(
    chatId: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Any:
    """
    Get chat by ID
    Retrieve specific chat information
    """
    try:
        chat_service_instance = get_chat_service(session)
        chat = chat_service_instance.get_chat_by_id(chatId)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        # Verify user belongs to the same tenant
        if str(chat.tenant_id) != str(current_user.tenant_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        stats = chat_service_instance.get_chat_stats(chatId)
        
        chat_response = ChatRead(
            id=chat.id,
            name=chat.name,
            system_prompt=chat.system_prompt,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            tenant_id=chat.tenant_id,
            session_count=stats["session_count"]
        )
        
        return DataResponse(
            data=chat_response,
            message="Chat retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chat: {str(e)}"
        )


@router.put("/{chatId}", response_model=DataResponse[ChatRead])
async def update_chat(
    chatId: str,
    chat_data: ChatUpdate,
    current_user: User = Depends(require_tenant_admin),
    session: Session = Depends(get_session)
) -> Any:
    """
    Update chat
    Update chat information (tenant admin only)
    """
    try:
        chat_service_instance = get_chat_service(session)
        # First verify chat exists and belongs to user's tenant
        existing_chat = chat_service_instance.get_chat_by_id(chatId)
        if not existing_chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        if str(existing_chat.tenant_id) != str(current_user.tenant_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        chat = chat_service_instance.update_chat(chatId, chat_data.dict(exclude_unset=True))
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        stats = chat_service_instance.get_chat_stats(chatId)
        
        chat_response = ChatRead(
            id=chat.id,
            name=chat.name,
            system_prompt=chat.system_prompt,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            tenant_id=chat.tenant_id,
            session_count=stats["session_count"]
        )
        
        return DataResponse(
            data=chat_response,
            message="Chat updated successfully"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update chat: {str(e)}"
        )


@router.delete("/{chatId}")
async def delete_chat(
    chatId: str,
    current_user: User = Depends(require_tenant_admin),
    session: Session = Depends(get_session)
) -> Any:
    """
    Delete chat
    Delete a chat and all associated sessions and messages (tenant admin only)
    """
    try:
        chat_service_instance = get_chat_service(session)
        # First verify chat exists and belongs to user's tenant
        existing_chat = chat_service_instance.get_chat_by_id(chatId)
        if not existing_chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        if str(existing_chat.tenant_id) != str(current_user.tenant_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        deleted = chat_service_instance.delete_chat_cascade(chatId)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete chat: {str(e)}"
        )