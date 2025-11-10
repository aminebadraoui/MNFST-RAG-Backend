"""
Authentication middleware for FastAPI
"""
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.jwt import jwt_service
from app.exceptions.auth import AuthenticationError, InvalidTokenError


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle authentication for protected routes
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and add authentication information if available
        
        Args:
            request: Incoming request
            call_next: Next middleware in the chain
            
        Returns:
            Response from the next middleware
        """
        # Skip authentication for certain paths
        if self._should_skip_auth(request.url.path):
            return await call_next(request)
        
        # Extract token from Authorization header
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            # No token provided, continue without authentication
            # The route will handle authentication if needed
            return await call_next(request)
        
        token = authorization.split(" ")[1]
        
        try:
            # Validate token
            payload = jwt_service.validate_access_token(token)
            if payload:
                # Add user info to request state
                request.state.user_id = payload.get("sub")
                request.state.user_email = payload.get("email")
                request.state.user_role = payload.get("role")
                request.state.tenant_id = payload.get("tenant_id")
                request.state.token_payload = payload
        except Exception:
            # Invalid token, continue without authentication
            # The route will handle authentication if needed
            pass
        
        return await call_next(request)
    
    def _should_skip_auth(self, path: str) -> bool:
        """
        Check if authentication should be skipped for the given path
        
        Args:
            path: Request path
            
        Returns:
            True if authentication should be skipped
        """
        # Exact match paths
        exact_match_paths = [
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        
        # Prefix match paths
        prefix_match_paths = [
            "/api/v1/auth/",
        ]
        
        # Check for exact matches first
        if path in exact_match_paths:
            return True
        
        # Then check for prefix matches
        for prefix_path in prefix_match_paths:
            if path.startswith(prefix_path):
                return True
        
        return False