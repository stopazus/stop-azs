"""Rate limiting middleware using slowapi."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from api.config import settings

logger = structlog.get_logger()

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT],
    storage_uri=settings.REDIS_URL,
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors.
    
    Args:
        request: The incoming request
        exc: The rate limit exception
        
    Returns:
        429 response with Retry-After header
    """
    logger.warning(
        "rate_limit_exceeded",
        client_ip=request.client.host if request.client else None,
        path=request.url.path,
    )
    
    return Response(
        content='{"detail": "Rate limit exceeded"}',
        status_code=429,
        headers={
            "Retry-After": str(exc.detail),
            "Content-Type": "application/json"
        }
    )
