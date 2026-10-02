"""FastAPI application entrypoint for Equestrian Compliance & Specification Auditor."""
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.audit_router import router as audit_router
from backend.app.api.rules_router import router as rules_router
from backend.app.api.vendor_router import router as vendor_router
from backend.app.core.config import settings
from backend.app.rag.vector_store import vector_store_manager

logger = logging.getLogger("equestrian_auditor")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Pre-warm directories, vector database, and knowledge base on startup."""
    logger.info("Initializing system directories and storage...")
    settings.ensure_directories()

    # Pre-index regulations if collection is empty
    try:
        count = vector_store_manager.client.count(
            collection_name=vector_store_manager.collection_name
        ).count
        if count == 0:
            logger.info("Pre-indexing regulatory markdown files into Qdrant...")
            vector_store_manager.index_all_regulations()
    except Exception as exc:
        logger.warning("Vector store warm-up note: %s", exc)

    logger.info("Equestrian Auditor backend ready.")
    yield
    logger.info("Shutting down Equestrian Auditor backend...")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Copilot for Luxury Equestrian Technical Wear Compliance & Specification Auditing",
    lifespan=lifespan,
)

# CORS Middleware for Next.js 14 frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount cropped technical sketches and figures
figures_path = Path(settings.FIGURE_EXPORT_DIR)
figures_path.mkdir(parents=True, exist_ok=True)
app.mount("/static/figures", StaticFiles(directory=str(figures_path)), name="figures")


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Standardized JSON response for HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": exc.status_code,
            "timestamp": datetime.now(UTC).isoformat(),
            "path": str(request.url),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Standardized JSON response for unexpected internal server errors."""
    logger.error("Unhandled exception on %s: %s", request.url, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred while processing the request.",
            "error": str(exc),
            "timestamp": datetime.now(UTC).isoformat(),
            "path": str(request.url),
        },
    )


@app.get("/api/health", tags=["System"])
@app.get("/api/v1/health", tags=["System"])
@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    """Health check endpoint reporting API and environment status."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
        "timestamp": datetime.now(UTC).isoformat(),
    }


# Include Core Feature Routers (Canonical v1 & Legacy Aliases)
for prefix in ("/api/v1", "/api"):
    app.include_router(audit_router, prefix=f"{prefix}/audit", tags=["Audit"])
    app.include_router(vendor_router, prefix=f"{prefix}/audit", tags=["Vendor"])
    app.include_router(rules_router, prefix=f"{prefix}/rules", tags=["Rules"])
