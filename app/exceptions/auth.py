"""
Authentication-related exceptions
"""
from fastapi import HTTPException, status


class AuthenticationError(HTTPException):
    """Base authentication exception"""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidCredentialsError(AuthenticationError):
    """Invalid credentials exception"""
    
    def __init__(self):
        super().__init__(detail="Invalid email or password")


class TokenExpiredError(AuthenticationError):
    """Token expired exception"""
    
    def __init__(self):
        super().__init__(detail="Token has expired")


class InvalidTokenError(AuthenticationError):
    """Invalid token exception"""
    
    def __init__(self):
        super().__init__(detail="Invalid token")


class MissingTokenError(AuthenticationError):
    """Missing token exception"""
    
    def __init__(self):
        super().__init__(detail="Authentication token is required")


class AuthorizationError(HTTPException):
    """Authorization exception"""
    
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class InsufficientRoleError(AuthorizationError):
    """Insufficient role exception"""
    
    def __init__(self, required_role: str):
        super().__init__(detail=f"Requires {required_role} role or higher")


class TenantAccessError(AuthorizationError):
    """Tenant access exception"""
    
    def __init__(self):
        super().__init__(detail="Access to this tenant's data is not allowed")


class ResourceOwnershipError(AuthorizationError):
    """Resource ownership exception"""
    
    def __init__(self):
        super().__init__(detail="Access to this resource is not allowed")


class PasswordValidationError(Exception):
    """Password validation exception"""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class UserNotFoundError(Exception):
    """User not found exception"""
    
    def __init__(self, message: str = "User not found"):
        self.message = message
        super().__init__(message)


class UserAlreadyExistsError(Exception):
    """User already exists exception"""
    
    def __init__(self, message: str = "User with this email already exists"):
        self.message = message
        super().__init__(message)