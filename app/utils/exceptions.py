"""
Custom exceptions
"""
from typing import Optional
from fastapi import HTTPException, status


class MNFSTRAGException(Exception):
    """Base exception for MNFST-RAG application"""
    
    def __init__(self, message: str, code: Optional[str] = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundError(MNFSTRAGException):
    """Exception raised when resource is not found"""
    
    def __init__(self, resource: str, identifier: Optional[str] = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, "NOT_FOUND")


class UnauthorizedError(MNFSTRAGException):
    """Exception raised for unauthorized access"""
    
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message, "UNAUTHORIZED")


class ForbiddenError(MNFSTRAGException):
    """Exception raised for forbidden access"""
    
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message, "FORBIDDEN")


class ValidationError(MNFSTRAGException):
    """Exception raised for validation errors"""
    
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, "VALIDATION_ERROR")


class BadRequestError(MNFSTRAGException):
    """Exception raised for bad requests"""
    
    def __init__(self, message: str = "Bad request"):
        super().__init__(message, "BAD_REQUEST")


class InternalServerError(MNFSTRAGException):
    """Exception raised for internal server errors"""
    
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, "INTERNAL_SERVER_ERROR")


def http_exception_from_error(error: MNFSTRAGException) -> HTTPException:
    """Convert custom exception to HTTPException"""
    
    status_map = {
        NotFoundError: status.HTTP_404_NOT_FOUND,
        UnauthorizedError: status.HTTP_401_UNAUTHORIZED,
        ForbiddenError: status.HTTP_403_FORBIDDEN,
        ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        BadRequestError: status.HTTP_400_BAD_REQUEST,
        InternalServerError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    
    http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    for error_type, status_code in status_map.items():
        if isinstance(error, error_type):
            http_status = status_code
            break
    
    return HTTPException(
        status_code=http_status,
        detail={
            "success": False,
            "error": {
                "code": error.code or "UNKNOWN_ERROR",
                "message": error.message
            }
        }
    )