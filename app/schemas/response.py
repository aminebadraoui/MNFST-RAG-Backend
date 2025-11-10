"""
Standardized response schemas
"""
from pydantic import BaseModel, Field
from typing import Any, Optional, Generic, TypeVar

T = TypeVar('T')

class DataResponse(BaseModel, Generic[T]):
    """Standardized successful response with data"""
    success: bool = Field(default=True, description="Whether the request was successful")
    data: T = Field(description="Response data")
    message: Optional[str] = Field(None, description="Success message")

class ErrorResponse(BaseModel):
    """Standardized error response"""
    success: bool = Field(default=False, description="Always false for error responses")
    error: dict = Field(description="Error details")
    message: Optional[str] = Field(None, description="Error message")