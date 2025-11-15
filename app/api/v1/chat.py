"""
Chat sessions and messages endpoints
"""
from fastapi import APIRouter, HTTPException, status, Query, Depends, Response
from fastapi.responses import StreamingResponse
from typing import Any, List
from sqlmodel import Session

from app.schemas.chat import (
    SessionRead, SessionCreate, MessageRead, MessageCreate,
    SendMessageRequest, StreamChunk
)
from app.schemas.response import DataResponse
from app.services.chat import get_chat_service
from app.database import get_session
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.utils.streaming import stream_response_as_sse, stream_error_as_sse

router = APIRouter()


@router.get("/", response_model=DataResponse[List[SessionRead]])
async def get_sessions(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    chat_id: str = Query(None, description="Chat ID to filter sessions"),
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
) -> Any:
    """
    Get chat sessions
    Retrieve all chat sessions for current user, optionally filtered by chat.
    If no sessions exist for the chat, creates a default session.
    """
    try:
        chat_service_instance = get_chat_service(db_session)
        sessions = chat_service_instance.get_chat_sessions(
            chat_id=chat_id,
            user_id=str(current_user.id)
        )
        
        # If no sessions exist for this chat and user, create a default session
        if chat_id and not sessions:
            try:
                # Verify the chat exists and belongs to the user's tenant
                chat = chat_service_instance.get_chat_by_id(chat_id)
                if chat and str(chat.tenant_id) == str(current_user.tenant_id):
                    default_session = chat_service_instance.create_session(
                        chat_id=chat_id,
                        user_id=str(current_user.id),
                        title="New Chat Session"
                    )
                    sessions = [default_session]
            except Exception as e:
                # Log the error but continue with empty sessions list
                print(f"Failed to create default session: {e}")
        
        session_reads = []
        for session in sessions:
            session_read = SessionRead(
                id=session.id,
                title=session.title,
                created_at=session.created_at,
                updated_at=session.updated_at,
                user_id=session.user_id,
                chat_id=session.chat_id
            )
            session_reads.append(session_read)
        
        return DataResponse(
            data=session_reads,
            message="Sessions retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sessions: {str(e)}"
        )


@router.post("/", response_model=DataResponse[SessionRead], status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
) -> Any:
    """
    Create chat session
    Create a new chat session for current user
    """
    try:
        chat_service_instance = get_chat_service(db_session)
        db_session = chat_service_instance.create_session(
            chat_id=str(session_data.chat_id),
            user_id=str(current_user.id),
            title=session_data.title
        )
        
        session_read = SessionRead(
            id=db_session.id,
            title=db_session.title,
            created_at=db_session.created_at,
            updated_at=db_session.updated_at,
            user_id=db_session.user_id,
            chat_id=db_session.chat_id
        )
        
        return DataResponse(
            data=session_read,
            message="Session created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@router.delete("/{sessionId}")
async def delete_session(
    sessionId: str,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
) -> Any:
    """
    Delete chat session
    Delete a chat session and all its messages
    """
    try:
        chat_service_instance = get_chat_service(db_session)
        # First verify session exists and belongs to user
        session_obj = chat_service_instance.get_session_by_id(sessionId)
        if not session_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if str(session_obj.user_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        deleted = chat_service_instance.delete_session_cascade(sessionId)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )


@router.get("/{sessionId}/messages", response_model=DataResponse[List[MessageRead]])
async def get_messages(
    sessionId: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
) -> Any:
    """
    Get chat messages
    Retrieve all messages in a chat session
    """
    try:
        chat_service_instance = get_chat_service(db_session)
        # First verify session exists and belongs to user
        session_obj = chat_service_instance.get_session_by_id(sessionId)
        if not session_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if str(session_obj.user_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        messages = chat_service_instance.get_session_messages(sessionId)
        
        message_reads = []
        for message in messages:
            message_read = MessageRead(
                id=message.id,
                session_id=message.session_id,
                content=message.content,
                role=message.role,
                timestamp=message.timestamp
            )
            message_reads.append(message_read)
        
        return DataResponse(
            data=message_reads,
            message="Messages retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve messages: {str(e)}"
        )


@router.post("/{sessionId}/messages", response_model=DataResponse[MessageRead], status_code=status.HTTP_201_CREATED)
async def send_message(
    sessionId: str,
    message_data: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
) -> Any:
    """
    Send message
    Send a message to a chat session
    """
    try:
        chat_service_instance = get_chat_service(db_session)
        # First verify session exists and belongs to user
        session_obj = chat_service_instance.get_session_by_id(sessionId)
        if not session_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if str(session_obj.user_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get the chat to retrieve system prompt
        chat = chat_service_instance.get_chat_by_id(str(session_obj.chat_id))
        system_prompt = chat.system_prompt if chat else None
        
        # Store the user message
        message = chat_service_instance.create_message(
            session_id=sessionId,
            content=message_data.content,
            role=message_data.role
        )
        
        # Create a static response message with all required data
        static_response_content = f"Message received, here is all the data I received: message: '{message_data.content}', user_id: '{current_user.id}', tenant_id: '{current_user.tenant_id}', session_id: '{sessionId}', system_prompt: '{system_prompt}'"
        
        # Create and store the assistant response
        assistant_message = chat_service_instance.create_message(
            session_id=sessionId,
            content=static_response_content,
            role="assistant"
        )
        
        message_read = MessageRead(
            id=assistant_message.id,
            session_id=assistant_message.session_id,
            content=assistant_message.content,
            role=assistant_message.role,
            timestamp=assistant_message.timestamp
        )
        
        return DataResponse(
            data=message_read,
            message="Message sent successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.post("/{sessionId}/messages/stream")
async def send_message_stream(
    sessionId: str,
    message_data: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
) -> StreamingResponse:
    """
    Send message with streaming
    Send a message to a chat session with streaming response using Server-Sent Events (SSE)
    """
    try:
        chat_service_instance = get_chat_service(db_session)
        # First verify session exists and belongs to user
        session_obj = chat_service_instance.get_session_by_id(sessionId)
        if not session_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if str(session_obj.user_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get the chat to retrieve system prompt
        chat = chat_service_instance.get_chat_by_id(str(session_obj.chat_id))
        system_prompt = chat.system_prompt if chat else None
        
        # Store the user message
        user_message = chat_service_instance.create_message(
            session_id=sessionId,
            content=message_data.content,
            role=message_data.role
        )
        
        # Create a static response with all required data
        static_response_content = f"Message received, here is all the data I received: message: '{message_data.content}', user_id: '{current_user.id}', tenant_id: '{current_user.tenant_id}', session_id: '{sessionId}', system_prompt: '{system_prompt}'"
        
        # Create and store the assistant response
        assistant_message = chat_service_instance.create_message(
            session_id=sessionId,
            content=static_response_content,
            role="assistant"
        )
        
        # Ensure we have a valid message ID - it should be populated after commit
        if not assistant_message.id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create message - no ID generated"
            )
        
        # Cast to UUID to satisfy type checker
        message_id = assistant_message.id  # Type: ignore
        
        # Create the streaming response
        async def generate_stream():
            try:
                async for chunk in stream_response_as_sse(
                    response_content=static_response_content,
                    message_id=message_id,
                    chunk_size=3,  # Send 3 words at a time
                    delay=0.1     # 100ms delay between chunks
                ):
                    yield chunk
            except Exception as e:
                # Stream error if something goes wrong
                async for error_chunk in stream_error_as_sse(str(e)):
                    yield error_chunk
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )