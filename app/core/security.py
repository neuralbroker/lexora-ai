"""Security utilities for authentication and authorization."""

from datetime import UTC, datetime, timedelta
from typing import Any, Optional
from uuid import uuid4

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def create_access_token(
    subject: str | Any,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict] = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        subject: Token subject (typically user ID)
        expires_delta: Optional expiration time delta
        additional_claims: Additional claims to include in token

    Returns:
        Encoded JWT token string
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

    to_encode = {"sub": str(subject), "type": "access", "jti": str(uuid4())}
    if additional_claims:
        to_encode.update(additional_claims)

    expire = datetime.now(UTC) + expires_delta
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    return encoded_jwt


def create_refresh_token(subject: str | Any) -> str:
    """Create a JWT refresh token."""
    expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    to_encode = {
        "sub": str(subject),
        "type": "refresh",
        "jti": str(uuid4()),
        "exp": expire,
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def get_token_ttl_seconds(payload: dict[str, Any]) -> int:
    """Return remaining token lifetime in whole seconds for blacklist TTLs."""
    exp = payload.get("exp")
    if exp is None:
        return 0

    try:
        expires_at = datetime.fromtimestamp(int(exp), tz=UTC)
    except (TypeError, ValueError, OSError):
        return 0

    remaining = expires_at - datetime.now(UTC)
    return max(int(remaining.total_seconds()), 0)


def verify_token_type(token: str, expected_type: str) -> dict[str, Any]:
    """
    Verify token type and return payload.

    Args:
        token: JWT token string
        expected_type: Expected token type (access or refresh)

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token type doesn't match
    """
    payload = decode_token(token)
    token_type = payload.get("type")

    if token_type != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type. Expected {expected_type}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload
