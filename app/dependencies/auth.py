"""
Authentication dependencies for FastAPI routes
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session

from app.database import get_session
from app.models.user import User, UserRole
from app.services.jwt import jwt_service
from app.services.auth import auth_service
from app.exceptions.auth import (
    AuthenticationError, 
    InvalidTokenError, 
    TokenExpiredError,
    InsufficientRoleError,
    TenantAccessError
)

# HTTP Bearer token scheme
security = HTTPBearer()


def get_token_from_credentials(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract token from HTTP Authorization header
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        Token string
    """
    return credentials.credentials


def get_current_user_token(
    token: str = Depends(get_token_from_credentials)
) -> dict:
    """
    Get current user token payload
    
    Args:
        token: JWT token
        
    Returns:
        Token payload
        
    Raises:
        AuthenticationError: If token is invalid or expired
    """
    payload = jwt_service.validate_access_token(token)
    if not payload:
        raise AuthenticationError(detail="Invalid or expired token")
    
    return payload


def get_current_user(
    token_payload: dict = Depends(get_current_user_token),
    session: Session = Depends(get_session)
) -> User:
    """
    Get current authenticated user
    
    Args:
        token_payload: Token payload
        session: Database session
        
    Returns:
        Current user object
        
    Raises:
        AuthenticationError: If user is not found
    """
    user_id = token_payload.get("sub")
    if not user_id:
        raise AuthenticationError(detail="Invalid token payload")
    
    from sqlmodel import select
    
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    
    if not user:
        raise AuthenticationError(detail="User not found")
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user
    
    Args:
        current_user: Current user
        
    Returns:
        Current active user
    """
    # Add any additional checks for user status if needed
    return current_user


def require_role(required_role: UserRole):
    """
    Create a dependency that requires a specific role or higher
    
    Args:
        required_role: Minimum required role
        
    Returns:
        Dependency function
    """
    def role_dependency(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        # Define role hierarchy
        role_hierarchy = {
            UserRole.USER: 0,
            UserRole.TENANT_ADMIN: 1,
            UserRole.SUPERADMIN: 2
        }
        
        user_level = role_hierarchy.get(current_user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        if user_level < required_level:
            raise InsufficientRoleError(required_role.value)
        
        return current_user
    
    return role_dependency


def require_tenant_access(
    current_user: User = Depends(get_current_active_user),
    tenant_id: Optional[str] = None
) -> User:
    """
    Ensure user has access to the specified tenant
    
    Args:
        current_user: Current user
        tenant_id: Tenant ID to check access for
        
    Returns:
        Current user if access is allowed
        
    Raises:
        TenantAccessError: If user doesn't have access to the tenant
    """
    # Superadmins can access any tenant
    if current_user.role == UserRole.SUPERADMIN:
        return current_user
    
    # For tenant admins and users, check if they belong to the specified tenant
    if tenant_id and str(current_user.tenant_id) != tenant_id:
        raise TenantAccessError()
    
    return current_user


def get_optional_current_user(
    token: Optional[str] = Depends(get_token_from_credentials)
) -> Optional[User]:
    """
    Get current user if token is provided, without raising exceptions
    
    Args:
        token: JWT token (optional)
        
    Returns:
        Current user if token is valid, None otherwise
    """
    if not token:
        return None
    
    try:
        payload = jwt_service.validate_access_token(token)
        if not payload:
            return None
        
        return auth_service.get_user_from_token(token)
    except Exception:
        return None


# Common role dependencies
require_superadmin = require_role(UserRole.SUPERADMIN)
require_tenant_admin = require_role(UserRole.TENANT_ADMIN)
require_user = require_role(UserRole.USER)