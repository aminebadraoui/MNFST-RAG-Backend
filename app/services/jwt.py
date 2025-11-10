"""
JWT service for token generation and validation
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt

from app.config import settings


class JWTService:
    """Service for JWT token operations"""
    
    @staticmethod
    def generate_access_token(
        user_id: str, 
        email: str, 
        role: str, 
        tenant_id: Optional[str] = None
    ) -> str:
        """
        Generate an access token
        
        Args:
            user_id: User ID
            email: User email
            role: User role
            tenant_id: Tenant ID (optional)
            
        Returns:
            JWT access token string
        """
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)
        
        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "tenant_id": tenant_id,
            "exp": expires_at,
            "iat": now,
            "type": "access"
        }
        
        return jwt.encode(
            payload, 
            settings.jwt_secret_key, 
            algorithm=settings.jwt_algorithm
        )
    
    @staticmethod
    def generate_refresh_token(user_id: str) -> str:
        """
        Generate a refresh token
        
        Args:
            user_id: User ID
            
        Returns:
            JWT refresh token string
        """
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=settings.jwt_refresh_token_expire_days)
        
        payload = {
            "sub": user_id,
            "exp": expires_at,
            "iat": now,
            "type": "refresh"
        }
        
        return jwt.encode(
            payload, 
            settings.jwt_secret_key, 
            algorithm=settings.jwt_algorithm
        )
    
    @staticmethod
    def validate_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a JWT token and return its payload
        
        Args:
            token: JWT token string
            
        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token, 
                settings.jwt_secret_key, 
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            # Token has expired
            return None
        except jwt.InvalidTokenError:
            # Token is invalid
            return None
    
    @staticmethod
    def validate_access_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Validate an access token and return its payload
        
        Args:
            token: JWT access token string
            
        Returns:
            Token payload if valid, None otherwise
        """
        payload = JWTService.validate_token(token)
        if payload and payload.get("type") == "access":
            return payload
        return None
    
    @staticmethod
    def validate_refresh_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a refresh token and return its payload
        
        Args:
            token: JWT refresh token string
            
        Returns:
            Token payload if valid, None otherwise
        """
        payload = JWTService.validate_token(token)
        if payload and payload.get("type") == "refresh":
            return payload
        return None
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[str]:
        """
        Generate a new access token using a refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token if refresh token is valid, None otherwise
        """
        payload = JWTService.validate_refresh_token(refresh_token)
        if not payload:
            return None
        
        # For a complete implementation, we would need to fetch user details
        # from the database using the user_id from the refresh token
        # For now, we'll return None to indicate this needs to be implemented
        # in the authentication service
        return None
    
    @staticmethod
    def get_token_expiration(token: str) -> Optional[datetime]:
        """
        Get the expiration time of a token
        
        Args:
            token: JWT token string
            
        Returns:
            Expiration datetime if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token, 
                settings.jwt_secret_key, 
                algorithms=[settings.jwt_algorithm],
                options={"verify_exp": False}  # Don't verify expiration
            )
            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                return datetime.fromtimestamp(exp_timestamp, timezone.utc)
            return None
        except jwt.InvalidTokenError:
            return None


# Global JWT service instance
jwt_service = JWTService()