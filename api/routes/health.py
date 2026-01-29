"""Health and readiness check endpoints."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
import structlog
import redis

from api.config import settings
from api.models.schemas import HealthResponse, ReadinessResponse

logger = structlog.get_logger()
router = APIRouter(prefix="/health", tags=["Health"])


# Import get_db from main module (will be set properly when app is initialized)
from api.main import get_db


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.
    
    Returns basic application status without checking dependencies.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        version=settings.APP_VERSION
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness check with dependency verification.
    
    Checks database and Redis connectivity.
    """
    db_status = "unknown"
    redis_status = "unknown"
    
    # Check database connectivity
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error("database_health_check_failed", error=str(e))
        db_status = "disconnected"
    
    # Check Redis connectivity
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        redis_status = "connected"
    except Exception as e:
        logger.error("redis_health_check_failed", error=str(e))
        redis_status = "disconnected"
    
    # Overall status
    overall_status = "ready" if (db_status == "connected" and redis_status == "connected") else "not_ready"
    
    # Return response even if not ready
    return ReadinessResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc),
        database=db_status,
        redis=redis_status
    )
