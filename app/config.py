"""
Application configuration settings
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = Field(default="MNFST-RAG API", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Database
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/mnfst_rag",
        description="Database connection URL"
    )
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origins"
    )
    
    # Supabase (optional)
    supabase_url: str = Field(default="", description="Supabase URL")
    supabase_key: str = Field(default="", description="Supabase API key")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()