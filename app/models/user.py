"""Pydantic models for API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# User models
class UserBase(BaseModel):
    """Base user model."""

    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Model for creating a new user."""

    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Model for updating user information."""

    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class UserResponse(UserBase):
    """Model for user response."""

    id: str
    is_active: bool
    is_admin: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Model for authentication tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Model for token payload."""

    sub: str
    exp: int
    type: str


# Document models
class DocumentBase(BaseModel):
    """Base document model."""

    filename: str


class DocumentUploadResponse(DocumentBase):
    """Model for document upload response."""

    id: str
    status: str
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentResponse(DocumentBase):
    """Model for document response."""

    id: str
    user_id: str
    file_type: str
    file_size: int
    status: str
    chunk_count: int
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentStatus(BaseModel):
    """Model for document processing status."""

    id: str
    status: str
    chunk_count: Optional[int] = None
    error_message: Optional[str] = None


# Chat models
class MessageBase(BaseModel):
    """Base message model."""

    content: str


class MessageCreate(MessageBase):
    """Model for creating a new message."""

    conversation_id: Optional[str] = None


class MessageResponse(MessageBase):
    """Model for message response."""

    id: str
    conversation_id: str
    role: str
    sources: Optional[list[dict]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationBase(BaseModel):
    """Base conversation model."""

    title: Optional[str] = None


class ConversationCreate(ConversationBase):
    """Model for creating a new conversation."""

    pass


class ConversationResponse(ConversationBase):
    """Model for conversation response."""

    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    """Model for chat request."""

    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[str] = None
    document_ids: Optional[list[str]] = None


class ChatResponse(BaseModel):
    """Model for chat response."""

    message: str
    conversation_id: str
    sources: list[dict]


# API Key models
class APIKeyCreate(BaseModel):
    """Model for creating an API key."""

    name: Optional[str] = None
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)


class APIKeyResponse(BaseModel):
    """Model for API key response."""

    id: str
    name: Optional[str]
    key: str  # Only shown once upon creation
    created_at: datetime
    expires_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# Health check models
class HealthCheck(BaseModel):
    """Model for health check response."""

    status: str
    version: str
    timestamp: datetime


# Error models
class ErrorDetail(BaseModel):
    """Model for error details."""

    code: str
    message: str
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Model for error response."""

    error: ErrorDetail
