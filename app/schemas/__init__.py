"""
Schemas package - API schemas only
"""
from .auth import LoginRequest, LoginResponse, RefreshTokenRequest, RefreshTokenResponse
from .user import UserRead, UserCreate, UserUpdate
from .tenant import TenantRead, TenantCreate, TenantUpdate
from .document import (
    DocumentRead, DocumentCreate, PresignedUrlResponse,
    RegisterUploadRequest, UploadStatusResponse, DocumentUploadStatus
)
from .social import SocialLinkRead, SocialLinkCreate, AddLinkRequest
from .chat import (
    SessionRead, SessionCreate, MessageRead, MessageCreate,
    SendMessageRequest, StreamChunk
)
from .response import DataResponse, ErrorResponse

__all__ = [
    # Auth schemas
    "LoginRequest",
    "LoginResponse",
    "RefreshTokenRequest",
    "RefreshTokenResponse",
    
    # User schemas
    "UserRead",
    "UserCreate",
    "UserUpdate",
    
    # Tenant schemas
    "TenantRead",
    "TenantCreate",
    "TenantUpdate",
    
    # Document schemas
    "DocumentRead",
    "DocumentCreate",
    "PresignedUrlResponse",
    "RegisterUploadRequest",
    "UploadStatusResponse",
    "DocumentUploadStatus",
    
    # Social schemas
    "SocialLinkRead",
    "SocialLinkCreate",
    "AddLinkRequest",
    
    # Chat schemas
    "SessionRead",
    "SessionCreate",
    "MessageRead",
    "MessageCreate",
    "SendMessageRequest",
    "StreamChunk",
    
    # Response schemas
    "DataResponse",
    "ErrorResponse",
]