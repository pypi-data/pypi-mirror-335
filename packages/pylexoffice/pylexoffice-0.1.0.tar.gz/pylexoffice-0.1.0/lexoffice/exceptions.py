from typing import Optional, Dict, Any
from .http import HTTPStatus, HTTPStatusMessages

class LexofficeApiError(Exception):
    """Base exception for Lexoffice API errors"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict[str, Any]] = None):
        if status_code:
            message = f"{message} ({status_code}: {HTTPStatusMessages.get_message(status_code)})"
        super().__init__(message)
        self.status_code = status_code
        self.response = response

class RateLimitExceeded(LexofficeApiError):
    """Raised when API rate limit is exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", response: Optional[Dict[str, Any]] = None):
        super().__init__(message, HTTPStatus.TOO_MANY_REQUESTS, response)

class ValidationError(LexofficeApiError):
    """Raised when request validation fails"""
    
    def __init__(self, message: str, response: Optional[Dict[str, Any]] = None):
        super().__init__(message, HTTPStatus.NOT_ACCEPTABLE, response)

class AuthenticationError(LexofficeApiError):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed", response: Optional[Dict[str, Any]] = None):
        super().__init__(message, HTTPStatus.UNAUTHORIZED, response)

class ResourceNotFoundError(LexofficeApiError):
    """Raised when a resource is not found"""
    
    def __init__(self, resource_id: str, response: Optional[Dict[str, Any]] = None):
        super().__init__(f"Resource not found: {resource_id}", HTTPStatus.NOT_FOUND, response)

class OptimisticLockingError(LexofficeApiError):
    """Raised when optimistic locking fails due to version mismatch"""
    
    def __init__(self, message: str = "Resource version conflict", response: Optional[Dict[str, Any]] = None):
        super().__init__(message, HTTPStatus.CONFLICT, response) 