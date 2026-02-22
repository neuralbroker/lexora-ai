"""Authentication endpoints."""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import AuthenticationError, ValidationError
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token_type,
)
from app.deps import DBSession, CurrentUser
from app.models.user import Token, UserCreate, UserResponse
from app.schemas.database import User

settings = get_settings()
logger = get_logger(__name__)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: DBSession,
) -> User:
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
    
    Returns:
        Created user
    """
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise ValidationError("Email already registered")

    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    logger.info("user_registered", user_id=user.id, email=user.email)

    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: DBSession,
) -> dict:
    """
    Login and get access token.
    
    Args:
        form_data: OAuth2 form with username (email) and password
        db: Database session
    
    Returns:
        Access and refresh tokens
    """
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise AuthenticationError("Incorrect email or password")

    if not user.is_active:
        raise AuthenticationError("User account is disabled")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    logger.info("user_logged_in", user_id=user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: DBSession,
) -> dict:
    """
    Refresh access token.
    
    Args:
        refresh_token: Refresh token
        db: Database session
    
    Returns:
        New access and refresh tokens
    """
    payload = verify_token_type(refresh_token, "refresh")
    user_id = payload.get("sub")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise AuthenticationError("Invalid refresh token")

    access_token = create_access_token(user.id)
    new_refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(
    current_user: CurrentUser,
) -> dict:
    """
    Logout (invalidate tokens on client side).
    
    Note: For production, implement token blacklist in Redis.
    """
    logger.info("user_logged_out", user_id=current_user.id)
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: CurrentUser,
) -> User:
    """Get current user information."""
    return current_user
