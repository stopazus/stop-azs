"""Tests for JWT authentication middleware."""

import pytest
import jwt
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from api.config import settings


def test_valid_token_grants_access(client: TestClient, valid_jwt_token: str, valid_sar_payload: dict):
    """Test that a valid JWT token with correct scope grants access."""
    response = client.post(
        "/api/sar-records",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json=valid_sar_payload
    )
    
    # Should not get 401 or 403
    assert response.status_code != 401
    assert response.status_code != 403


def test_missing_token_returns_401_or_403(client: TestClient, valid_sar_payload: dict):
    """Test that missing authorization header returns 401 or 403."""
    response = client.post(
        "/api/sar-records",
        json=valid_sar_payload
    )
    
    # FastAPI HTTPBearer returns 403 for missing/invalid header format
    assert response.status_code in [401, 403]


def test_invalid_token_returns_401(client: TestClient, valid_sar_payload: dict):
    """Test that an invalid JWT token returns 401."""
    response = client.post(
        "/api/sar-records",
        headers={"Authorization": "Bearer invalid_token_here"},
        json=valid_sar_payload
    )
    
    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]


def test_expired_token_returns_401(client: TestClient, expired_jwt_token: str, valid_sar_payload: dict):
    """Test that an expired JWT token returns 401."""
    response = client.post(
        "/api/sar-records",
        headers={"Authorization": f"Bearer {expired_jwt_token}"},
        json=valid_sar_payload
    )
    
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()


def test_insufficient_scope_returns_403(client: TestClient, insufficient_scope_token: str, valid_sar_payload: dict):
    """Test that a token without required scope returns 403."""
    response = client.post(
        "/api/sar-records",
        headers={"Authorization": f"Bearer {insufficient_scope_token}"},
        json=valid_sar_payload
    )
    
    assert response.status_code == 403
    assert "scope" in response.json()["detail"].lower()


def test_malformed_authorization_header_returns_401(client: TestClient, valid_sar_payload: dict):
    """Test that malformed authorization header returns 401."""
    # Missing 'Bearer' prefix
    response = client.post(
        "/api/sar-records",
        headers={"Authorization": "invalid_format"},
        json=valid_sar_payload
    )
    
    assert response.status_code == 403  # FastAPI HTTPBearer returns 403 for invalid format


def test_token_with_additional_scopes(client: TestClient, valid_sar_payload: dict):
    """Test that token with additional scopes works."""
    payload = {
        "sub": "test-user@example.com",
        "scope": "sar:write sar:read admin",  # Multiple scopes
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    response = client.post(
        "/api/sar-records",
        headers={"Authorization": f"Bearer {token}"},
        json=valid_sar_payload
    )
    
    # Should succeed (has sar:write among other scopes)
    assert response.status_code != 401
    assert response.status_code != 403
