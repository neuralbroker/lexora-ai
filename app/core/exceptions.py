"""Custom exceptions for the application."""

from typing import Any, Optional


class LexoraException(Exception):
    """Base exception for Lexora AI."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(LexoraException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", details: Optional[dict] = None):
        super().__init__(message, status_code=401, details=details)


class AuthorizationError(LexoraException):
    """Raised when user is not authorized to perform an action."""

    def __init__(self, message: str = "Not authorized", details: Optional[dict] = None):
        super().__init__(message, status_code=403, details=details)


class NotFoundError(LexoraException):
    """Raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found", details: Optional[dict] = None):
        super().__init__(message, status_code=404, details=details)


class ValidationError(LexoraException):
    """Raised when validation fails."""

    def __init__(self, message: str = "Validation failed", details: Optional[dict] = None):
        super().__init__(message, status_code=422, details=details)


class DocumentProcessingError(LexoraException):
    """Raised when document processing fails."""

    def __init__(self, message: str = "Document processing failed", details: Optional[dict] = None):
        super().__init__(message, status_code=500, details=details)


class RateLimitError(LexoraException):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", details: Optional[dict] = None):
        super().__init__(message, status_code=429, details=details)


class ServiceUnavailableError(LexoraException):
    """Raised when a service is unavailable."""

    def __init__(self, message: str = "Service unavailable", details: Optional[dict] = None):
        super().__init__(message, status_code=503, details=details)
