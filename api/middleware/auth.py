"""JWT bearer token authentication middleware."""

from typing import Optional
import jwt
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import structlog

from api.config import settings

logger = structlog.get_logger()
security = HTTPBearer()


class AuthenticationError(HTTPException):
    """Raised when authentication fails."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    """Raised when authorization fails (insufficient scope)."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Verify JWT bearer token and extract claims.
    
    Args:
        credentials: HTTP authorization credentials from request
        
    Returns:
        Token payload/claims dictionary
        
    Raises:
        AuthenticationError: If token is invalid or expired
        AuthorizationError: If token lacks required scope
    """
    token = credentials.credentials
    
    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Check required scope
        scopes = payload.get("scope", "").split()
        if settings.JWT_REQUIRED_SCOPE not in scopes:
            logger.warning(
                "insufficient_scope",
                required_scope=settings.JWT_REQUIRED_SCOPE,
                provided_scopes=scopes,
                subject=payload.get("sub")
            )
            raise AuthorizationError(
                f"Insufficient scope. Required: {settings.JWT_REQUIRED_SCOPE}"
            )
        
        logger.debug(
            "token_verified",
            subject=payload.get("sub"),
            scopes=scopes
        )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("token_expired")
        raise AuthenticationError("Token has expired")
        
    except jwt.InvalidTokenError as e:
        logger.warning("invalid_token", error=str(e))
        raise AuthenticationError(f"Invalid token: {str(e)}")


def get_submitter_identity(token_payload: dict) -> str:
    """
    Extract submitter identity from token payload.
    
    Args:
        token_payload: Decoded JWT payload
        
    Returns:
        Submitter identity (subject claim)
    """
    return token_payload.get("sub", "unknown")
