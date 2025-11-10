"""
Authentication service for coordinating authentication flows
"""
from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlmodel import Session, select

from app.models.user import User, UserRole
from app.services.jwt import jwt_service
from app.services.password import password_service
from app.database import get_session


class AuthenticationService:
    """Service for authentication operations"""
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password
        
        Args:
            email: User email
            password: User password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        # Get database session
        session = next(get_session())
        
        try:
            # Find user by email
            statement = select(User).where(User.email == email)
            user = session.exec(statement).first()
            
            # Check if user exists and password is correct
            if user and hasattr(user, 'password_hash') and user.password_hash:
                if password_service.verify_password(password, user.password_hash):
                    # Update last login
                    user.last_login = datetime.now(timezone.utc)
                    session.add(user)
                    session.commit()
                    session.refresh(user)
                    return user
            
            return None
        finally:
            session.close()
    
    @staticmethod
    def create_tokens(user: User) -> Tuple[str, str]:
        """
        Create access and refresh tokens for a user
        
        Args:
            user: User object
            
        Returns:
            Tuple of (access_token, refresh_token)
        """
        access_token = jwt_service.generate_access_token(
            user_id=str(user.id),
            email=user.email,
            role=user.role.value,
            tenant_id=str(user.tenant_id) if user.tenant_id else None
        )
        
        refresh_token = jwt_service.generate_refresh_token(str(user.id))
        
        return access_token, refresh_token
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[Tuple[str, str]]:
        """
        Refresh an access token using a refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Tuple of (new_access_token, new_refresh_token) if successful, None otherwise
        """
        # Validate refresh token
        payload = jwt_service.validate_refresh_token(refresh_token)
        if not payload:
            return None
        
        # Get user from database
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        session = next(get_session())
        
        try:
            # Find user by ID
            statement = select(User).where(User.id == user_id)
            user = session.exec(statement).first()
            
            if not user:
                return None
            
            # Create new tokens (token rotation)
            new_access_token, new_refresh_token = AuthenticationService.create_tokens(user)
            
            return new_access_token, new_refresh_token
        finally:
            session.close()
    
    @staticmethod
    def get_user_from_token(token: str) -> Optional[User]:
        """
        Get user from access token
        
        Args:
            token: Access token
            
        Returns:
            User object if token is valid, None otherwise
        """
        # Validate access token
        payload = jwt_service.validate_access_token(token)
        if not payload:
            return None
        
        # Get user from database
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        session = next(get_session())
        
        try:
            # Find user by ID
            statement = select(User).where(User.id == user_id)
            user = session.exec(statement).first()
            
            return user
        finally:
            session.close()
    
    @staticmethod
    def create_user_with_password(
        email: str, 
        password: str, 
        name: str, 
        role: UserRole,
        tenant_id: Optional[str] = None
    ) -> User:
        """
        Create a new user with a hashed password
        
        Args:
            email: User email
            password: Plain text password
            name: User name
            role: User role
            tenant_id: Tenant ID (optional)
            
        Returns:
            Created user object
        """
        # Validate password strength
        is_valid, error_message = password_service.validate_password_strength(password)
        if not is_valid:
            raise ValueError(error_message)
        
        # Hash password
        password_hash = password_service.hash_password(password)
        
        # Create user
        user = User(
            email=email,
            name=name,
            role=role,
            tenant_id=tenant_id,
            password_hash=password_hash
        )
        
        # Save to database
        session = next(get_session())
        
        try:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


# Global authentication service instance
auth_service = AuthenticationService()