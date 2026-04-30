"""
app/schemas/document.py
───────────────────────
Pydantic request/response schemas for document endpoints.
"""

from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    original_filename: str
    mime_type: str
    file_size: int
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class OTPRequestResponse(BaseModel):
    message: str
    document_id: str
    expires_in_minutes: int
    # Only populated when DEBUG=True and email is not configured
    otp_code: str | None = None


class OTPVerifyRequest(BaseModel):
    otp_code: str


class DownloadTokenResponse(BaseModel):
    message: str
    filename: str
