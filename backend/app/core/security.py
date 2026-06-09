import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TokenType = Literal["access", "refresh"]


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(subject: str, expires_delta: timedelta, token_type: TokenType) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        # Ensures uniqueness even when two tokens for the same user are minted
        # within the same second (iat/exp would otherwise be identical).
        "jti": secrets.token_hex(16),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: int) -> str:
    return _create_token(
        str(user_id), timedelta(minutes=settings.access_token_expire_minutes), "access"
    )


def create_refresh_token(user_id: int) -> str:
    return _create_token(
        str(user_id), timedelta(days=settings.refresh_token_expire_days), "refresh"
    )


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None


def hash_token(token: str) -> str:
    """One-way hash used to store opaque/JWT tokens (refresh, password reset) at rest."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_url_safe_token() -> str:
    return secrets.token_urlsafe(48)


def generate_link_code() -> str:
    return secrets.token_hex(4).upper()
