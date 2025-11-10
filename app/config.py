"""
Application configuration settings
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
import secrets


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = Field(default="MNFST-RAG API", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Database
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/mnfst_rag",
        description="Database connection URL (use Supabase URL in production)"
    )
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origins"
    )
    
    # JWT Settings
    jwt_secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for JWT token signing"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: int = Field(
        default=60, description="Access token expiration time in minutes"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=30, description="Refresh token expiration time in days"
    )
    
    # Password Settings
    password_min_length: int = Field(default=8, description="Minimum password length")
    password_salt_rounds: int = Field(default=12, description="bcrypt salt rounds")
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False


# Global settings instance
settings = Settings()