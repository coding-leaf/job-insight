"""FastAPI main application entrypoint."""

# ruff: noqa: E402

import logging
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

# Ensure 'backend' directory is in sys.path so 'from app...' works regardless of cwd
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.mongodb import db_manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan managing database lifecycle."""
    logger.info("Initializing %s ...", settings.PROJECT_NAME)
    connected = await db_manager.connect()
    if connected:
        db = db_manager.get_db()
        if db is not None:
            count = await db.jobs.count_documents({})
            logger.info("Primary MongoDB connected. Collection 'jobs' contains %d documents.", count)
            if count == 0:
                logger.warning(
                    "MongoDB collection 'jobs' is empty! Seed with: python backend/app/db/seed.py"
                )
    else:
        logger.warning(
            "Primary datastore MongoDB could not be connected at %s. "
            "Please start MongoDB container (docker compose up -d) and seed data.",
            settings.MONGODB_URL,
        )
    yield
    logger.info("Shutting down %s ...", settings.PROJECT_NAME)
    await db_manager.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": f"Validation Error: {exc.errors()}",
            "data": None,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled server exception: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": f"Internal Server Error: {exc!s}",
            "data": None,
        },
    )


# Health check
@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, Any]:
    db = db_manager.get_db()
    mongo_status = "disconnected"
    doc_count = 0
    indexes: list[str] = []
    if db is not None:
        try:
            await db.command("ping")
            mongo_status = "connected"
            doc_count = await db.jobs.count_documents({})
            idx_info = await db.jobs.index_information()
            indexes = list(idx_info.keys())
        except Exception as e:
            mongo_status = f"error: {e}"

    is_healthy = mongo_status == "connected" and doc_count > 0
    return {
        "status": "ok" if is_healthy else "degraded",
        "app": settings.PROJECT_NAME,
        "database": {
            "engine": "MongoDB",
            "status": mongo_status,
            "collection": "jobs",
            "document_count": doc_count,
            "indexes": indexes,
            "primary_datastore": True,
        },
    }


# Mount API V1 Router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
