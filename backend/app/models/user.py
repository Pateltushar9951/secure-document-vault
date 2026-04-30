"""
app/models/user.py
──────────────────
MongoDB document model for users.
"""

from datetime import datetime, timezone
from mongoengine import Document, StringField, BooleanField, DateTimeField


class User(Document):
    """User model for MongoDB."""
    
    email = StringField(required=True, unique=True, index=True)
    hashed_password = StringField(required=True)
    is_active = BooleanField(default=True)
    email_verified = BooleanField(default=True)
    email_verified_at = DateTimeField(null=True)
    email_verification_otp_hash = StringField(null=True)
    email_verification_expires_at = DateTimeField(null=True)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    meta = {
        'collection': 'users',
        'indexes': ['email'],
    }

    def to_dict(self):
        return {
            'id': str(self.id),
            'email': self.email,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'email_verified_at': self.email_verified_at.isoformat() if self.email_verified_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<User id={self.id!r} email={self.email!r}>"

