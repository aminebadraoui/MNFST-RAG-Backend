"""
User service for managing user operations
"""
from typing import Optional
from sqlmodel import Session, select
from uuid import UUID

from app.models.user import User, UserRole
from app.services.base import BaseService
from app.services.password import password_service


class UserService(BaseService):
    """Service for user operations"""
    
    def create_user(
        self, 
        email: str, 
        password: str, 
        name: str, 
        role: UserRole,
        tenant_id: Optional[str] = None
    ) -> User:
        """
        Create a new user with a hashed password (without transaction management)
        
        Args:
            email: User email
            password: Plain text password
            name: User name
            role: User role
            tenant_id: Tenant ID (optional)
            
        Returns:
            Created user object
            
        Raises:
            ValueError: If user email already exists or password is invalid
        """
        # Check if user email already exists
        statement = select(User).where(User.email == email)
        existing_user = self.session.exec(statement).first()
        if existing_user:
            raise ValueError(f"User with email '{email}' already exists")
        
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
        
        # Add to session (but don't commit - let the coordinator handle it)
        self.session.add(user)
        self.session.flush()  # Get ID without committing
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User object if found, None otherwise
        """
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).first()
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            email: User email
            
        Returns:
            User object if found, None otherwise
        """
        statement = select(User).where(User.email == email)
        user = self.session.exec(statement).first()
        return user


# Global user service instance
user_service = UserService()