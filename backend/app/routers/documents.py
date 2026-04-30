"""
app/routers/documents.py
─────────────────────────
Document management endpoints for MongoDB.
"""

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import Response

from app.config import get_settings
from app.models.document import FileDocument
from app.models.user import User
from app.schemas.document import (
    DocumentResponse,
    OTPRequestResponse,
    OTPVerifyRequest,
)
from app.services.auth_service import get_current_user
from app.services.email_service import send_otp_email
from app.services.encryption_service import decrypt_file, encrypt_file
from app.services.otp_service import generate_otp, verify_otp
from app.utils.file_validator import validate_upload

settings = get_settings()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])


# ── Helper ────────────────────────────────────────────────────
def _get_document_or_404(doc_id: str, user_id: str) -> FileDocument:
    """Fetch a document owned by the user or raise 404."""
    try:
        doc = FileDocument.objects.get(id=doc_id, owner_id=user_id)
    except FileDocument.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )
    return doc


# ── Upload ────────────────────────────────────────────────────
@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and encrypt a document",
)
async def upload_document(
    file: UploadFile = File(..., description="PDF, PNG, or JPEG file (max 10 MB)"),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a file to the vault with MongoDB storage.
    """
    raw_bytes = await validate_upload(file)
    original_name = file.filename or "unnamed_file"

    import mimetypes as _mt
    mime = file.content_type or _mt.guess_type(original_name)[0] or "application/octet-stream"

    encrypted_bytes = encrypt_file(raw_bytes)
    stored_name = f"{uuid.uuid4().hex}.enc"
    dest_path: Path = settings.storage_path / stored_name

    dest_path.write_bytes(encrypted_bytes)
    logger.info("Stored encrypted file: %s (%d bytes)", stored_name, len(encrypted_bytes))

    doc = FileDocument(
        owner_id=str(current_user.id),
        original_filename=original_name,
        stored_filename=stored_name,
        mime_type=mime,
        file_size=len(raw_bytes),
    )
    doc.save()

    return DocumentResponse(
        id=str(doc.id),
        owner_id=str(doc.owner_id),
        original_filename=doc.original_filename,
        stored_filename=doc.stored_filename,
        mime_type=doc.mime_type,
        file_size=doc.file_size,
        uploaded_at=doc.uploaded_at,
    )


# ── List ──────────────────────────────────────────────────────
@router.get(
    "/",
    response_model=list[DocumentResponse],
    summary="List all documents in the vault",
)
def list_documents(
    current_user: User = Depends(get_current_user),
):
    """
    Return a list of all documents uploaded by the authenticated user.
    """
    docs = FileDocument.objects(owner_id=str(current_user.id)).order_by('-uploaded_at')
    return [
        DocumentResponse(
            id=str(doc.id),
            owner_id=str(doc.owner_id),
            original_filename=doc.original_filename,
            stored_filename=doc.stored_filename,
            mime_type=doc.mime_type,
            file_size=doc.file_size,
            uploaded_at=doc.uploaded_at,
        )
        for doc in docs
    ]


# ── Delete ────────────────────────────────────────────────────
@router.delete(
    "/{doc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document from the vault",
)
def delete_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Permanently delete a document and its encrypted file.
    """
    doc = _get_document_or_404(doc_id, str(current_user.id))

    file_path = settings.storage_path / doc.stored_filename
    if file_path.exists():
        file_path.unlink()
        logger.info("Deleted encrypted file: %s", doc.stored_filename)

    doc.delete()


# ── Request Download (send OTP) ───────────────────────────────
@router.post(
    "/download/request/{doc_id}",
    response_model=OTPRequestResponse,
    summary="Request a download — triggers OTP generation and email",
)
def request_download(
    doc_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Initiate a secure download with MongoDB.
    """
    doc = _get_document_or_404(doc_id, str(current_user.id))

    otp_code = generate_otp(
        user_id=str(current_user.id),
        document_id=str(doc.id),
    )

    email_sent = send_otp_email(
        recipient_email=current_user.email,
        otp_code=otp_code,
        filename=doc.original_filename,
    )

    expose_otp = settings.DEBUG and not email_sent
    logger.info(
        "Download requested for doc %s by user %s — email_sent=%s",
        doc_id, current_user.email, email_sent,
    )

    return OTPRequestResponse(
        message=(
            "OTP sent to your email. Submit it within "
            f"{settings.OTP_EXPIRE_MINUTES} minutes."
            if email_sent
            else (
                f"[DEBUG] Email not configured. OTP returned in this response. "
                f"Expires in {settings.OTP_EXPIRE_MINUTES} minutes."
            )
        ),
        document_id=str(doc.id),
        expires_in_minutes=settings.OTP_EXPIRE_MINUTES,
        otp_code=otp_code if expose_otp else None,
    )


# ── Verify OTP → Download file ────────────────────────────────
@router.post(
    "/download/verify/{doc_id}",
    summary="Submit OTP to download the decrypted file",
    responses={
        200: {"description": "Decrypted file bytes", "content": {"application/octet-stream": {}}},
        400: {"description": "Invalid or expired OTP"},
        404: {"description": "Document not found"},
    },
)
def verify_and_download(
    doc_id: str,
    payload: OTPVerifyRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Complete the secure download flow with MongoDB.
    """
    doc = _get_document_or_404(doc_id, str(current_user.id))

    verify_otp(
        user_id=str(current_user.id),
        document_id=str(doc.id),
        otp_code=payload.otp_code,
    )

    file_path = settings.storage_path / doc.stored_filename
    if not file_path.exists():
        logger.error("Encrypted file missing from storage: %s", doc.stored_filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Encrypted file not found on server.",
        )

    encrypted_bytes = file_path.read_bytes()
    decrypted_bytes = decrypt_file(encrypted_bytes)

    logger.info(
        "Download completed: doc=%s user=%s size=%d bytes",
        doc_id, current_user.email, len(decrypted_bytes),
    )

    return Response(
        content=decrypted_bytes,
        media_type=doc.mime_type,
        headers={
            "Content-Disposition": f'attachment; filename="{doc.original_filename}"',
            "Content-Length": str(len(decrypted_bytes)),
        },
    )
