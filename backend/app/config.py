"""
app/config.py
─────────────
Central settings loaded from the .env file.
All app-wide configuration constants live here.
"""

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── App ───────────────────────────────────────────────────
    APP_NAME: str = "Secure Document Vault"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ── Security ──────────────────────────────────────────────
    FERNET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ── Database (MongoDB Atlas) ──────────────────────────────
    MONGODB_URI: str = "mongodb+srv://pateltushar9951_db_user:Uz4fSnM99yr6eVK9@cluster.mongodb.net/secure_vault?retryWrites=true&w=majority"
    MONGODB_DB_NAME: str = "secure_vault"

    # ── Storage ───────────────────────────────────────────────
    STORAGE_DIR: str = "storage"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_MIME_TYPES: str = "application/pdf,image/png,image/jpeg"

    # ── OTP ───────────────────────────────────────────────────
    OTP_EXPIRE_MINUTES: int = 5
    OTP_LENGTH: int = 6

    # ── Email / SMTP ──────────────────────────────────────────
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Derived helpers ───────────────────────────────────────
    @property
    def allowed_mime_list(self) -> list[str]:
        return [m.strip() for m in self.ALLOWED_MIME_TYPES.split(",")]

    @property
    def max_file_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def storage_path(self) -> Path:
        p = Path(self.STORAGE_DIR)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def email_configured(self) -> bool:
        return bool(self.SMTP_HOST and self.SMTP_USERNAME and self.SMTP_PASSWORD)


@lru_cache
def get_settings() -> Settings:
    return Settings()
