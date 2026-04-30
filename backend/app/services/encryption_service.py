"""
app/services/encryption_service.py
────────────────────────────────────
AES-based symmetric file encryption using Fernet (cryptography library).

Fernet provides:
  • AES-128-CBC encryption
  • HMAC-SHA256 authentication
  • Timestamp (allows token TTL checks)

The key is loaded once from settings and reused for all operations.
"""

from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException, status

from app.config import get_settings

settings = get_settings()


def _get_fernet() -> Fernet:
    """Return a Fernet instance initialised with the app key."""
    try:
        return Fernet(settings.FERNET_KEY.encode())
    except Exception:
        raise RuntimeError(
            "Invalid FERNET_KEY in .env — generate one with: "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )


def encrypt_file(data: bytes) -> bytes:
    """
    Encrypt raw file bytes.

    Args:
        data: plaintext file bytes

    Returns:
        Fernet-encrypted ciphertext bytes
    """
    fernet = _get_fernet()
    return fernet.encrypt(data)


def decrypt_file(encrypted_data: bytes) -> bytes:
    """
    Decrypt Fernet-encrypted bytes.

    Args:
        encrypted_data: ciphertext bytes from storage

    Returns:
        Original plaintext file bytes

    Raises:
        HTTPException 500 if decryption fails (corrupt data or wrong key).
    """
    fernet = _get_fernet()
    try:
        return fernet.decrypt(encrypted_data)
    except InvalidToken:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File decryption failed — data may be corrupt.",
        )
