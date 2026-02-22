"""Dependency injection for FastAPI."""

from typing import Annotated, Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.security import verify_token_type
from app.models.user import TokenPayload
from app.schemas.database import get_db

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> "User":
    """
    Get current authenticated user from JWT token.
    
    This dependency validates the access token and retrieves
    the user from the database.
    """
    from app.schemas.database import User
    from sqlalchemy import select

    payload = verify_token_type(token, "access")
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    return user


async def get_current_active_user(
    current_user: Annotated["User", Depends(get_current_user)],
) -> "User":
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    return current_user


async def get_optional_current_user(
    token: Annotated[Optional[str], Depends(oauth2_scheme)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> Optional["User"]:
    """Get current user if authenticated, otherwise return None."""
    if token is None:
        return None

    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None


def require_admin(current_user: Annotated["User", Depends(get_current_user)]) -> "User":
    """Require admin privileges."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


# Type alias for dependency injection
User = dict  # Placeholder for type hint
DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[dict, Depends(get_current_user)]
ActiveUser = Annotated[dict, Depends(get_current_active_user)]
