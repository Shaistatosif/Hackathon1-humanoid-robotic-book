"""Health check API router.

Provides endpoints for monitoring application health and dependencies.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])


class HealthStatus(BaseModel):
    """Health check response model."""

    status: str
    timestamp: str
    version: str
    environment: str
    checks: dict[str, dict[str, str | bool | int]]


class SimpleHealth(BaseModel):
    """Simple health check response."""

    status: str


@router.get("", response_model=SimpleHealth)
async def health_check():
    """Basic health check endpoint.

    Returns a simple status indicating the API is running.
    Use /health/detailed for comprehensive health information.
    """
    return SimpleHealth(status="healthy")


@router.get("/live", response_model=SimpleHealth)
async def liveness_check():
    """Kubernetes-style liveness probe.

    Indicates if the application is running.
    Returns 200 if the process is alive.
    """
    return SimpleHealth(status="alive")


@router.get("/ready", response_model=SimpleHealth)
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Kubernetes-style readiness probe.

    Indicates if the application is ready to receive traffic.
    Checks database connectivity.
    """
    try:
        # Test database connection
        await db.execute(text("SELECT 1"))
        return SimpleHealth(status="ready")
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return SimpleHealth(status="not_ready")


@router.get("/detailed", response_model=HealthStatus)
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check with dependency status.

    Checks all external dependencies and returns comprehensive status.
    """
    checks: dict[str, dict[str, str | bool | int]] = {}

    # Check database
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = {"status": "healthy", "connected": True}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        checks["database"] = {"status": "unhealthy", "connected": False, "error": str(e)}

    # Check Qdrant (vector database)
    try:
        from src.core.qdrant import get_qdrant_client

        client = get_qdrant_client()
        if client:
            # Try to get collections list
            collections = client.get_collections()
            checks["qdrant"] = {
                "status": "healthy",
                "connected": True,
                "collections": len(collections.collections),
            }
        else:
            checks["qdrant"] = {"status": "not_configured", "connected": False}
    except Exception as e:
        logger.warning(f"Qdrant health check failed: {e}")
        checks["qdrant"] = {"status": "unhealthy", "connected": False, "error": str(e)}

    # Check Gemini API
    try:
        from src.core.gemini import get_gemini_client

        gemini_client = get_gemini_client()
        if gemini_client:
            checks["gemini"] = {"status": "configured", "connected": True}
        else:
            checks["gemini"] = {"status": "not_configured", "connected": False}
    except Exception as e:
        logger.warning(f"Gemini health check failed: {e}")
        checks["gemini"] = {"status": "unhealthy", "connected": False, "error": str(e)}

    # Determine overall status
    critical_checks = ["database"]
    overall_status = "healthy"

    for check_name in critical_checks:
        if check_name in checks and checks[check_name].get("status") == "unhealthy":
            overall_status = "unhealthy"
            break

    return HealthStatus(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        version="0.1.0",
        environment="development" if settings.debug else "production",
        checks=checks,
    )
