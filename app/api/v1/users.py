"""
User management endpoints
"""
from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import Any, List
from sqlmodel import select

from app.schemas.user import UserRead, UserCreate, UserUpdate
from app.schemas.response import DataResponse
from app.models.user import User, UserRole
from app.dependencies.auth import (
    get_current_active_user,
    require_tenant_admin,
    require_superadmin,
    require_tenant_access
)
from app.services.auth import auth_service
from app.database import get_session
from app.exceptions.auth import (
    UserNotFoundError,
    UserAlreadyExistsError,
    AuthorizationError
)

router = APIRouter()


@router.get("/", response_model=DataResponse[List[UserRead]])
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(require_tenant_admin),
    session = Depends(get_session)
) -> Any:
    """
    Get users
    Retrieve all users for current tenant (tenant admin only)
    """
    try:
        # Build query based on user role
        if current_user.role == UserRole.SUPERADMIN:
            # Superadmins can see all users
            statement = select(User).offset((page - 1) * limit).limit(limit)
        else:
            # Tenant admins can only see users in their tenant
            statement = select(User).where(
                User.tenant_id == current_user.tenant_id
            ).offset((page - 1) * limit).limit(limit)
        
        users = session.exec(statement).all()
        
        # Convert to UserRead schema
        user_data = [
            UserRead(
                id=str(user.id),
                email=user.email,
                name=user.name,
                role=user.role.value,
                tenant_id=str(user.tenant_id) if user.tenant_id else None,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            for user in users
        ]
        
        return DataResponse(
            data=user_data,
            message="Users retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving users: {str(e)}"
        )


@router.post("/", response_model=DataResponse[UserRead], status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_tenant_admin),
    session = Depends(get_session)
) -> Any:
    """
    Create user
    Create a new user in current tenant (tenant admin only)
    """
    try:
        # Check if user already exists
        existing_user = session.exec(
            select(User).where(User.email == user_data.email)
        ).first()
        
        if existing_user:
            raise UserAlreadyExistsError()
        
        # Determine tenant_id for new user
        tenant_id = None
        if current_user.role == UserRole.SUPERADMIN:
            # Superadmin can create users for any tenant
            tenant_id = user_data.tenant_id
        else:
            # Tenant admin can only create users in their own tenant
            tenant_id = current_user.tenant_id
        
        # Create user with password
        user = auth_service.create_user_with_password(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name,
            role=user_data.role,
            tenant_id=str(tenant_id) if tenant_id else None
        )
        
        user_data = UserRead(
            id=str(user.id),
            email=user.email,
            name=user.name,
            role=user.role.value,
            tenant_id=str(user.tenant_id) if user.tenant_id else None,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
        return DataResponse(
            data=user_data,
            message="User created successfully"
        )
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating user: {str(e)}"
        )


@router.get("/{userId}", response_model=DataResponse[UserRead])
async def get_user(
    userId: str,
    current_user: User = Depends(get_current_active_user),
    session = Depends(get_session)
) -> Any:
    """
    Get user by ID
    Retrieve specific user information
    """
    try:
        # Find user
        statement = select(User).where(User.id == userId)
        user = session.exec(statement).first()
        
        if not user:
            raise UserNotFoundError()
        
        # Check authorization
        if current_user.role == UserRole.USER:
            # Users can only see their own profile
            if str(user.id) != str(current_user.id):
                raise AuthorizationError()
        elif current_user.role == UserRole.TENANT_ADMIN:
            # Tenant admins can only see users in their tenant
            if str(user.tenant_id) != str(current_user.tenant_id):
                raise AuthorizationError()
        # Superadmins can see any user
        
        user_data = UserRead(
            id=str(user.id),
            email=user.email,
            name=user.name,
            role=user.role.value,
            tenant_id=str(user.tenant_id) if user.tenant_id else None,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
        return DataResponse(
            data=user_data,
            message="User retrieved successfully"
        )
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except AuthorizationError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving user: {str(e)}"
        )


@router.put("/{userId}", response_model=DataResponse[UserRead])
async def update_user(
    userId: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    session = Depends(get_session)
) -> Any:
    """
    Update user
    Update user information
    """
    try:
        # Find user
        statement = select(User).where(User.id == userId)
        user = session.exec(statement).first()
        
        if not user:
            raise UserNotFoundError()
        
        # Check authorization
        if current_user.role == UserRole.USER:
            # Users can only update their own profile
            if str(user.id) != str(current_user.id):
                raise AuthorizationError()
        elif current_user.role == UserRole.TENANT_ADMIN:
            # Tenant admins can only update users in their tenant
            if str(user.tenant_id) != str(current_user.tenant_id):
                raise AuthorizationError()
        # Superadmins can update any user
        
        # Update user fields
        if user_data.name is not None:
            user.name = user_data.name
        if user_data.role is not None and current_user.role in [UserRole.TENANT_ADMIN, UserRole.SUPERADMIN]:
            user.role = user_data.role
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        user_data = UserRead(
            id=str(user.id),
            email=user.email,
            name=user.name,
            role=user.role.value,
            tenant_id=str(user.tenant_id) if user.tenant_id else None,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
        return DataResponse(
            data=user_data,
            message="User updated successfully"
        )
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except AuthorizationError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating user: {str(e)}"
        )


@router.delete("/{userId}")
async def delete_user(
    userId: str,
    current_user: User = Depends(require_tenant_admin),
    session = Depends(get_session)
) -> Any:
    """
    Delete user
    Delete a user from current tenant (tenant admin only)
    """
    try:
        # Find user
        statement = select(User).where(User.id == userId)
        user = session.exec(statement).first()
        
        if not user:
            raise UserNotFoundError()
        
        # Check authorization
        if current_user.role == UserRole.TENANT_ADMIN:
            # Tenant admins can only delete users in their tenant
            if str(user.tenant_id) != str(current_user.tenant_id):
                raise AuthorizationError()
        # Superadmins can delete any user
        
        # Prevent self-deletion
        if str(user.id) == str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        # Delete user
        session.delete(user)
        session.commit()
        
        from fastapi import Response
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except AuthorizationError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting user: {str(e)}"
        )