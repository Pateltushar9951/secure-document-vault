"""
app/models/document.py
──────────────────────
MongoDB document models for documents and OTPs.
"""

from datetime import datetime, timezone
from mongoengine import Document, StringField, IntField, DateTimeField, BooleanField


class FileDocument(Document):
    """Document metadata model for MongoDB."""
    
    owner_id = StringField(required=True, index=True)
    original_filename = StringField(required=True)
    stored_filename = StringField(required=True, unique=True)
    mime_type = StringField(required=True)
    file_size = IntField(required=True)  # bytes
    uploaded_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    meta = {
        'collection': 'documents',
        'indexes': ['owner_id', 'stored_filename'],
    }

    def to_dict(self):
        return {
            'id': str(self.id),
            'owner_id': self.owner_id,
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
        }

    def __repr__(self) -> str:
        return f"<FileDocument id={self.id!r} name={self.original_filename!r}>"


class OTP(Document):
    """One-Time Password model for MongoDB."""
    
    user_id = StringField(required=True, index=True)
    document_id = StringField(required=True)
    purpose = StringField(required=True, default="download")
    otp_hash = StringField(required=True)
    expires_at = DateTimeField(required=True)
    is_used = BooleanField(default=False)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    meta = {
        'collection': 'otps',
        'indexes': ['user_id', 'document_id', 'purpose', 'created_at'],
    }

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'document_id': self.document_id,
            'is_used': self.is_used,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
        }

    def __repr__(self) -> str:
        return f"<OTP id={self.id!r} used={self.is_used}>"

