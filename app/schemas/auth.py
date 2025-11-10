"""
Authentication schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

from .user import UserRead


class LoginRequest(BaseModel):
    """Login request model"""
    email: str = Field(description="User email")
    password: str = Field(description="User password")


class Tokens(BaseModel):
    """JWT tokens model"""
    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    expires_in: int = Field(description="Access token expiration time in seconds")


class LoginResponse(BaseModel):
    """Login response model"""
    user: UserRead = Field(description="User information")
    tokens: Tokens = Field(description="JWT tokens")


class RefreshTokenRequest(BaseModel):
    """Refresh token request model"""
    refresh_token: str = Field(description="JWT refresh token")


class RefreshTokenResponse(BaseModel):
    """Refresh token response model"""
    access_token: str = Field(description="New JWT access token")
    expires_in: int = Field(description="Access token expiration time in seconds")


class SuccessResponse(BaseModel):
    """Success response model"""
    success: bool = Field(default=True, description="Whether the request was successful")
    message: str = Field(description="Success message")