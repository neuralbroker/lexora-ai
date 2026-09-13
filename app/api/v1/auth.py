"""Authentication endpoints."""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.core.exceptions import AuthenticationError, ValidationError
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    get_token_ttl_seconds,
    verify_password,
    verify_token_type,
)
from app.deps import CurrentUser, DBSession, oauth2_scheme
from app.models.user import Token, UserCreate, UserResponse
from app.schemas.database import User

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
    db: DBSession,
    form_data: OAuth2PasswordRequestForm = Depends(),
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
    token_id = payload.get("jti")
    cache_service = None
    if token_id:
        from app.services.cache_service import get_cache_service

        cache_service = await get_cache_service()
        if await cache_service.exists(f"token_blacklist:{token_id}"):
            raise AuthenticationError("Refresh token has been revoked")

    user_id = payload.get("sub")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise AuthenticationError("Invalid refresh token")

    access_token = create_access_token(user.id)
    new_refresh_token = create_refresh_token(user.id)

    if token_id and cache_service is not None:
        ttl = get_token_ttl_seconds(payload)
        if ttl > 0:
            await cache_service.set(f"token_blacklist:{token_id}", {"revoked": True}, expire=ttl)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(
    current_user: CurrentUser,
    token: str = Depends(oauth2_scheme),
) -> dict:
    """Logout and revoke the current access token until it naturally expires."""
    payload = verify_token_type(token, "access")
    token_id = payload.get("jti")
    ttl = get_token_ttl_seconds(payload)

    if token_id and ttl > 0:
        from app.services.cache_service import get_cache_service

        cache_service = await get_cache_service()
        await cache_service.set(
            f"token_blacklist:{token_id}",
            {"revoked": True, "user_id": current_user.id},
            expire=ttl,
        )

    logger.info("user_logged_out", user_id=current_user.id)
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: CurrentUser,
) -> User:
    """Get current user information."""
    return current_user
