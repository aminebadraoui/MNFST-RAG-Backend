"""
Authentication endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any

from app.schemas.auth import (
    LoginRequest, LoginResponse, RefreshTokenRequest,
    RefreshTokenResponse, SuccessResponse
)
from app.schemas.response import DataResponse
from app.schemas.user import UserRead
from app.services.auth import auth_service
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.exceptions.auth import (
    InvalidCredentialsError,
    InvalidTokenError,
    AuthenticationError
)
from app.config import settings

router = APIRouter()


@router.post("/login", response_model=DataResponse[LoginResponse])
async def login(request: LoginRequest) -> Any:
    """
    User login
    Authenticate user with email and password, return JWT tokens
    """
    try:
        # Authenticate user
        user = auth_service.authenticate_user(request.email, request.password)
        if not user:
            raise InvalidCredentialsError()
        
        # Generate tokens
        access_token, refresh_token = auth_service.create_tokens(user)
        
        # Convert user to UserRead schema
        user_read = UserRead(
            id=str(user.id),
            email=user.email,
            name=user.name,
            role=user.role.value,
            tenant_id=str(user.tenant_id) if user.tenant_id else None,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
        # Create response
        tokens = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": settings.jwt_access_token_expire_minutes * 60
        }
        
        return DataResponse(
            data=LoginResponse(user=user_read, tokens=tokens),
            message="Login successful"
        )
    
    except InvalidCredentialsError:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during login: {str(e)}"
        )


@router.post("/refresh", response_model=DataResponse[RefreshTokenResponse])
async def refresh_token(request: RefreshTokenRequest) -> Any:
    """
    Refresh access token
    Refresh JWT access token using refresh token
    """
    try:
        # Log the incoming request for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Refresh token request received: {request}")
        
        # Check if refresh token is provided
        if not request.refresh_token:
            logger.error("No refresh token provided in request")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Refresh token is required"
            )
        
        # Refresh tokens
        tokens = auth_service.refresh_access_token(request.refresh_token)
        if not tokens:
            logger.error("Invalid refresh token")
            raise InvalidTokenError()
        
        access_token, refresh_token = tokens
        
        logger.info("Token refreshed successfully")
        
        return DataResponse(
            data=RefreshTokenResponse(
                access_token=access_token,
                expires_in=settings.jwt_access_token_expire_minutes * 60
            ),
            message="Token refreshed successfully"
        )
    
    except InvalidTokenError:
        raise
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error during token refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during token refresh: {str(e)}"
        )


@router.post("/logout", response_model=DataResponse[dict])
async def logout(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    User logout
    Logout user and invalidate tokens
    """
    # With stateless JWT tokens, we don't need to do anything server-side
    # The client should discard the tokens
    # In a more advanced implementation, we might maintain a blacklist
    
    return DataResponse(
        data={},
        message="Logged out successfully"
    )


@router.get("/me", response_model=DataResponse[UserRead])
async def get_current_user(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current user
    Get information about the currently authenticated user
    """
    return DataResponse(
        data=UserRead(
            id=str(current_user.id),
            email=current_user.email,
            name=current_user.name,
            role=current_user.role.value,
            tenant_id=str(current_user.tenant_id) if current_user.tenant_id else None,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at
        ),
        message="User retrieved successfully"
    )