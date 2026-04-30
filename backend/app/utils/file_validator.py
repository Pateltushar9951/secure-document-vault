"""
app/utils/file_validator.py
────────────────────────────
Validates uploaded files for:
  • MIME type (checked from actual file bytes, not just the extension)
  • File size limit

Uses the `imghdr` / `sndhdr` stdlib approach via mimetypes + magic-byte sniffing.
No external `python-magic` / `libmagic` required — uses a lightweight
pure-Python implementation via the `mimetypes` + a small magic-bytes map.
"""

import mimetypes
import struct
from fastapi import HTTPException, UploadFile, status
from app.config import get_settings

settings = get_settings()

# ── Magic-byte signatures for supported types ─────────────────
# Maps (offset, signature_bytes) → canonical MIME type
_MAGIC: list[tuple[int, bytes, str]] = [
    (0, b"%PDF",              "application/pdf"),
    (0, b"\x89PNG\r\n\x1a\n", "image/png"),
    (0, b"\xff\xd8\xff",      "image/jpeg"),  # JPEG
]


def _sniff_mime(data: bytes) -> str | None:
    """
    Sniff the MIME type from the first bytes of a file.
    Returns the MIME string or None if unrecognised.
    """
    for offset, sig, mime in _MAGIC:
        end = offset + len(sig)
        if len(data) >= end and data[offset:end] == sig:
            return mime
    return None


async def validate_upload(file: UploadFile, settings=settings) -> bytes:
    """
    Read the entire upload into memory, then validate:
      1. File size ≤ MAX_FILE_SIZE_MB
      2. MIME type is in ALLOWED_MIME_TYPES (checked via magic bytes)

    Returns:
        The raw file bytes (so callers don't need to re-read the stream).

    Raises:
        HTTPException 413 — file too large
        HTTPException 415 — unsupported media type
    """
    contents = await file.read()

    # ── Size check ────────────────────────────────────────────
    if len(contents) > settings.max_file_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"File too large. Maximum allowed size is "
                f"{settings.MAX_FILE_SIZE_MB} MB."
            ),
        )

    # ── MIME sniff ────────────────────────────────────────────
    detected_mime = _sniff_mime(contents)
    if detected_mime is None:
        detected_mime = (
            mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"
        )

    if detected_mime not in settings.allowed_mime_list:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"File type '{detected_mime}' is not allowed. "
                f"Accepted types: {', '.join(settings.allowed_mime_list)}"
            ),
        )

    return contents
