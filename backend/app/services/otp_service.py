"""
app/services/otp_service.py
────────────────────────────
Generates, stores, and verifies single-use OTPs for download requests.

Flow:
  1. generate_otp()  → creates a numeric OTP, hashes it, saves to DB
  2. verify_otp()    → checks hash + expiry + is_used flag, marks used
"""

import logging
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
import bcrypt as _bcrypt

from app.config import get_settings
from app.models.document import OTP

settings = get_settings()
logger = logging.getLogger(__name__)


def _generate_numeric_otp(length: int) -> str:
    """Return a cryptographically secure numeric OTP string."""
    upper = 10 ** length
    return str(secrets.randbelow(upper)).zfill(length)


def generate_otp(user_id: str, document_id: str) -> str:
    """
    Generate a new OTP for (user, document), persist a hashed copy,
    and return the plaintext OTP for delivery.
    """
    # Invalidate any previous unused OTPs for this document
    OTP.objects(
        user_id=user_id,
        document_id=document_id,
        is_used=False,
    ).delete()

    plaintext = _generate_numeric_otp(settings.OTP_LENGTH)
    otp_hash = _bcrypt.hashpw(plaintext.encode("utf-8"), _bcrypt.gensalt(rounds=10)).decode("utf-8")
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)

    otp_record = OTP(
        user_id=user_id,
        document_id=document_id,
        otp_hash=otp_hash,
        expires_at=expires_at,
    )
    otp_record.save()

    if settings.DEBUG:
        logger.warning(
            "[DEBUG] OTP for document %s --> %s  (expires in %d min)",
            document_id,
            plaintext,
            settings.OTP_EXPIRE_MINUTES,
        )

    return plaintext


def verify_otp(user_id: str, document_id: str, otp_code: str) -> None:
    """
    Verify the submitted OTP for MongoDB.
    """
    try:
        record = OTP.objects(
            user_id=user_id,
            document_id=document_id,
            is_used=False,
        ).order_by('-created_at').first()
    except OTP.DoesNotExist:
        record = None

    invalid_exc = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired OTP.",
    )

    if record is None:
        raise invalid_exc

    # Check expiry
    now = datetime.now(timezone.utc)
    expires = record.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if now > expires:
        raise invalid_exc

    # Verify hash
    try:
        if not _bcrypt.checkpw(otp_code.encode("utf-8"), record.otp_hash.encode("utf-8")):
            raise invalid_exc
    except Exception:
        raise invalid_exc

    # Mark as used
    record.is_used = True
    record.save()
