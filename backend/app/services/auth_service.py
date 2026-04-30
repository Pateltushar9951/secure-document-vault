"""
app/services/auth_service.py
────────────────────────────
Handles password hashing, JWT creation, and JWT verification.
Also provides the FastAPI dependency `get_current_user`.
"""

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
import bcrypt as _bcrypt

from app.config import get_settings
from app.models.user import User

settings = get_settings()

# ── Password hashing ──────────────────────────────────────────
# Using bcrypt directly (bypassing passlib) for Python 3.14 + bcrypt 5.x compat

def hash_password(plain: str) -> str:
    """Return a bcrypt hash of the given plaintext password."""
    return _bcrypt.hashpw(plain.encode("utf-8"), _bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the stored bcrypt hash."""
    try:
        return _bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ── JWT ───────────────────────────────────────────────────────
def create_access_token(subject: str) -> tuple[str, int]:
    """
    Create a signed JWT.

    Returns:
        (token_string, expire_seconds)
    """
    expire_seconds = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    expire_at = datetime.now(timezone.utc) + timedelta(seconds=expire_seconds)
    payload = {
        "sub": subject,          # user id
        "exp": expire_at,
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, expire_seconds


def decode_access_token(token: str) -> str:
    """
    Decode and validate a JWT.

    Returns:
        subject (user id) from the token

    Raises:
        HTTPException 401 on any failure.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception


# ── FastAPI dependency ─────────────────────────────────────────
_bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> User:
    """
    FastAPI dependency — extracts and validates the Bearer token,
    then returns the corresponding active User from MongoDB.
    """
    user_id = decode_access_token(credentials.credentials)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
