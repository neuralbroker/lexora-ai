"""Unit tests for core exceptions."""

import pytest
from app.core.exceptions import (
    LexoraException,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    DocumentProcessingError,
)


class TestLexoraException:
    """Tests for LexoraException base class."""

    def test_exception_creation(self):
        """Test basic exception creation."""
        exc = LexoraException("Test error", status_code=500)
        assert exc.message == "Test error"
        assert exc.status_code == 500
        assert exc.details == {}

    def test_exception_with_details(self):
        """Test exception with details."""
        exc = LexoraException(
            "Test error",
            status_code=400,
            details={"field": "email", "reason": "invalid"}
        )
        assert exc.details["field"] == "email"

    def test_exception_str(self):
        """Test exception string representation."""
        exc = LexoraException("Test error")
        assert str(exc) == "Test error"


class TestAuthenticationError:
    """Tests for AuthenticationError."""

    def test_default_values(self):
        """Test default status code."""
        exc = AuthenticationError()
        assert exc.status_code == 401

    def test_custom_message(self):
        """Test custom message."""
        exc = AuthenticationError("Invalid credentials")
        assert exc.message == "Invalid credentials"


class TestNotFoundError:
    """Tests for NotFoundError."""

    def test_status_code(self):
        """Test default status code."""
        exc = NotFoundError("Resource not found")
        assert exc.status_code == 404


class TestValidationError:
    """Tests for ValidationError."""

    def test_status_code(self):
        """Test default status code."""
        exc = ValidationError("Invalid input")
        assert exc.status_code == 422