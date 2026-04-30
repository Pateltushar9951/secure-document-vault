"""
app/routers/health.py
──────────────────────
Simple health-check endpoint.
"""

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    timestamp: str


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Returns server status and timestamp. Use this to verify the API is running.",
)
def health_check():
    from app.config import get_settings
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
