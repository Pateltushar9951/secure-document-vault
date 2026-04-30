"""
app/schemas/user.py
───────────────────
Pydantic request/response schemas for auth endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        errors = []
        if not any(c.isupper() for c in v):
            errors.append("at least one uppercase letter")
        if not any(c.islower() for c in v):
            errors.append("at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            errors.append("at least one digit")
        if errors:
            raise ValueError("Password must contain: " + ", ".join(errors))
        return v


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class EmailVerificationRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(min_length=6, max_length=6)


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class RegistrationResponse(BaseModel):
    message: str
    email: EmailStr
    verification_required: bool = True
    expires_in_minutes: int
    verification_code: str | None = None


class VerificationResponse(BaseModel):
    message: str
    email: EmailStr
    email_verified: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    id: str
    email: str
    is_active: bool
    email_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}
