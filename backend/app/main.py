"""
app/main.py
────────────
FastAPI application factory.

Creates the app, registers middleware, includes all routers,
and creates all database tables on startup.
"""

import io
import logging
import sys
from contextlib import asynccontextmanager

# Force UTF-8 output so emoji in log messages don't crash on Windows (cp1252)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import get_settings
from app.database import connect_db, disconnect_db
# Import all models so mongoengine knows about them
from app.models import user, document  # noqa: F401
from app.routers import auth, documents, health

# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

settings = get_settings()

# ── Rate limiter ──────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])


# ── Lifespan (startup / shutdown) ─────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────
    logger.info("[START] %s v%s is starting up...", settings.APP_NAME, settings.APP_VERSION)
    logger.info("[STORAGE] Directory: %s", settings.storage_path.resolve())

    # Create DB tables (idempotent)
    connect_db()
    logger.info("[DB] Connected to MongoDB Atlas.")

    if settings.DEBUG:
        logger.warning(
            "[WARNING] DEBUG mode is ON -- OTPs will be printed to this console. "
            "Never run in DEBUG mode in production."
        )

    yield

    # ── Shutdown ─────────────────────────────────────────────
    disconnect_db()
    logger.info("👋  Shutting down %s.", settings.APP_NAME)


# ── App factory ───────────────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "A secure personal document vault with AES encryption, "
            "JWT authentication, and OTP-verified downloads.\n\n"
            "**Flow**: Register → Login → Upload → Request Download → Verify OTP → Receive File"
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    @app.get("/", summary="API Root")
    def api_root():
        return {
            "message": f"{settings.APP_NAME} API is running.",
            "health": "/health",
            "docs": "/docs",
        }

    # ── Middleware ────────────────────────────────────────────
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.DEBUG else settings.frontend_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Global error handler ──────────────────────────────────
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception on %s %s", request.method, request.url)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An internal server error occurred."},
        )

    # ── Routers ───────────────────────────────────────────────
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(documents.router)

    return app


app = create_app()
