"""
Authentication utility functions
"""
from typing import Optional, Dict, Any
from fastapi import Request

from app.services.jwt import jwt_service
from app.exceptions.auth import InvalidTokenError


def extract_token_from_request(request: Request) -> Optional[str]:
    """
    Extract JWT token from request headers
    
    Args:
        request: FastAPI Request object
        
    Returns:
        Token string if found, None otherwise
    """
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    return authorization.split(" ")[1]


def get_token_payload_from_request(request: Request) -> Optional[Dict[str, Any]]:
    """
    Get token payload from request
    
    Args:
        request: FastAPI Request object
        
    Returns:
        Token payload if valid, None otherwise
    """
    token = extract_token_from_request(request)
    if not token:
        return None
    
    return jwt_service.validate_access_token(token)


def is_token_expired(token: str) -> bool:
    """
    Check if a token is expired
    
    Args:
        token: JWT token string
        
    Returns:
        True if token is expired, False otherwise
    """
    payload = jwt_service.validate_token(token)
    return payload is None


def get_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract user ID from token
    
    Args:
        token: JWT token string
        
    Returns:
        User ID if token is valid, None otherwise
    """
    payload = jwt_service.validate_access_token(token)
    if not payload:
        return None
    
    return payload.get("sub")


def get_user_role_from_token(token: str) -> Optional[str]:
    """
    Extract user role from token
    
    Args:
        token: JWT token string
        
    Returns:
        User role if token is valid, None otherwise
    """
    payload = jwt_service.validate_access_token(token)
    if not payload:
        return None
    
    return payload.get("role")


def get_tenant_id_from_token(token: str) -> Optional[str]:
    """
    Extract tenant ID from token
    
    Args:
        token: JWT token string
        
    Returns:
        Tenant ID if token is valid, None otherwise
    """
    payload = jwt_service.validate_access_token(token)
    if not payload:
        return None
    
    return payload.get("tenant_id")


def has_required_role(user_role: str, required_role: str) -> bool:
    """
    Check if user has the required role or higher
    
    Args:
        user_role: Current user role
        required_role: Required role
        
    Returns:
        True if user has required role or higher, False otherwise
    """
    from app.models.user import UserRole
    
    # Define role hierarchy
    role_hierarchy = {
        UserRole.USER.value: 0,
        UserRole.TENANT_ADMIN.value: 1,
        UserRole.SUPERADMIN.value: 2
    }
    
    user_level = role_hierarchy.get(user_role, 0)
    required_level = role_hierarchy.get(required_role, 0)
    
    return user_level >= required_level


def can_access_tenant(user_tenant_id: Optional[str], target_tenant_id: Optional[str], user_role: str) -> bool:
    """
    Check if user can access the specified tenant
    
    Args:
        user_tenant_id: User's tenant ID
        target_tenant_id: Target tenant ID
        user_role: User's role
        
    Returns:
        True if user can access tenant, False otherwise
    """
    from app.models.user import UserRole
    
    # Superadmins can access any tenant
    if user_role == UserRole.SUPERADMIN.value:
        return True
    
    # For other roles, check if they belong to the target tenant
    return str(user_tenant_id) == str(target_tenant_id)


def can_access_resource(user_id: str, resource_user_id: str, user_role: str) -> bool:
    """
    Check if user can access a resource owned by another user
    
    Args:
        user_id: Current user ID
        resource_user_id: Resource owner's user ID
        user_role: User's role
        
    Returns:
        True if user can access resource, False otherwise
    """
    from app.models.user import UserRole
    
    # Superadmins can access any resource
    if user_role == UserRole.SUPERADMIN.value:
        return True
    
    # Users can only access their own resources
    return str(user_id) == str(resource_user_id)