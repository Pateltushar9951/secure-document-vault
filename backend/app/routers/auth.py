"""
app/routers/auth.py
────────────────────
Authentication endpoints for MongoDB.
"""

import logging
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from mongoengine import NotUniqueError
import bcrypt as _bcrypt

from app.config import get_settings
from app.models.user import User
from app.schemas.user import (
    EmailVerificationRequest,
    RegistrationResponse,
    TokenResponse,
    ResendVerificationRequest,
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    VerificationResponse,
)
from app.services.auth_service import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.services.email_service import send_verification_email

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


def _generate_numeric_otp(length: int) -> str:
    upper = 10 ** length
    return str(secrets.randbelow(upper)).zfill(length)


def _start_email_verification(user: User) -> str:
    otp_code = _generate_numeric_otp(settings.OTP_LENGTH)
    user.email_verified = False
    user.email_verified_at = None
    user.email_verification_otp_hash = _bcrypt.hashpw(
        otp_code.encode("utf-8"),
        _bcrypt.gensalt(rounds=10),
    ).decode("utf-8")
    user.email_verification_expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.OTP_EXPIRE_MINUTES
    )
    user.save()
    return otp_code


def _verify_email_otp(user: User, otp_code: str) -> None:
    invalid_exc = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired verification code.",
    )

    if user.email_verified:
        return

    if not user.email_verification_otp_hash or not user.email_verification_expires_at:
        raise invalid_exc

    expires_at = user.email_verification_expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > expires_at:
        raise invalid_exc

    try:
        if not _bcrypt.checkpw(
            otp_code.encode("utf-8"),
            user.email_verification_otp_hash.encode("utf-8"),
        ):
            raise invalid_exc
    except Exception:
        raise invalid_exc

    user.email_verified = True
    user.email_verified_at = datetime.now(timezone.utc)
    user.email_verification_otp_hash = None
    user.email_verification_expires_at = None
    user.save()


# ── Register ──────────────────────────────────────────────────
@router.post(
    "/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(payload: UserRegisterRequest):
    """
    Create a new user account.

    - **email**: must be a valid email address (unique)
    - **password**: min 8 chars, must contain upper, lower, and digit
    """
    try:
        user = User(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            email_verified=False,
        )
        user.save()
        otp_code = _start_email_verification(user)
        email_sent = send_verification_email(
            recipient_email=user.email,
            otp_code=otp_code,
        )

        logger.info("New user registered: %s", user.email)
        verification_code = otp_code if settings.DEBUG and not email_sent else None
        return RegistrationResponse(
            message=(
                "Verification code sent to your email. "
                f"Enter it within {settings.OTP_EXPIRE_MINUTES} minutes."
                if email_sent
                else (
                    "Verification email not sent. "
                    f"Use the code shown in debug mode within {settings.OTP_EXPIRE_MINUTES} minutes."
                )
            ),
            email=user.email,
            verification_required=True,
            expires_in_minutes=settings.OTP_EXPIRE_MINUTES,
            verification_code=verification_code,
        )
    except NotUniqueError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )


@router.post(
    "/verify-email",
    response_model=VerificationResponse,
    summary="Verify a newly registered email address",
)
def verify_email(payload: EmailVerificationRequest):
    try:
        user = User.objects.get(email=payload.email)
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code.",
        )

    _verify_email_otp(user, payload.otp_code)

    return VerificationResponse(
        message="Email verified successfully. You can now sign in.",
        email=user.email,
        email_verified=True,
    )


@router.post(
    "/resend-verification",
    response_model=RegistrationResponse,
    summary="Resend the email verification code",
)
def resend_verification(payload: ResendVerificationRequest):
    try:
        user = User.objects.get(email=payload.email)
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found.",
        )

    if user.email_verified:
        return RegistrationResponse(
            message="Email is already verified.",
            email=user.email,
            verification_required=False,
            expires_in_minutes=0,
            verification_code=None,
        )

    otp_code = _start_email_verification(user)
    email_sent = send_verification_email(
        recipient_email=user.email,
        otp_code=otp_code,
    )

    return RegistrationResponse(
        message=(
            "Verification code sent to your email. "
            f"Enter it within {settings.OTP_EXPIRE_MINUTES} minutes."
            if email_sent
            else (
                "Verification email not sent. "
                f"Use the code shown in debug mode within {settings.OTP_EXPIRE_MINUTES} minutes."
            )
        ),
        email=user.email,
        verification_required=True,
        expires_in_minutes=settings.OTP_EXPIRE_MINUTES,
        verification_code=otp_code if settings.DEBUG and not email_sent else None,
    )


# ── Login ─────────────────────────────────────────────────────
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive a JWT",
)
def login(payload: UserLoginRequest):
    """
    Authenticate with email and password.

    Returns a **Bearer JWT** to include in the `Authorization` header.
    """
    try:
        user = User.objects.get(email=payload.email)
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email address is not verified. Check your inbox for the OTP.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    token, expires_in = create_access_token(subject=str(user.id))
    logger.info("User logged in: %s", user.email)
    return TokenResponse(access_token=token, expires_in=expires_in)


# ── Profile ───────────────────────────────────────────────────
@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
def get_profile(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's profile information."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        is_active=current_user.is_active,
        email_verified=current_user.email_verified,
        created_at=current_user.created_at,
    )
