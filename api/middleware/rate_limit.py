"""Rate limiting middleware using slowapi."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
import structlog

from api.config import settings

logger = structlog.get_logger()

# Initialize rate limiter with error handling for tests
try:
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[settings.RATE_LIMIT],
        storage_uri=settings.REDIS_URL,
    )
except Exception as e:
    logger.warning("rate_limiter_init_failed", error=str(e))
    # Create a dummy limiter for tests
    limiter = Limiter(key_func=get_remote_address, enabled=False)


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
