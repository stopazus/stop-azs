"""Tests for health check endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_health_check_returns_200(client: TestClient):
    """Test basic health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data


def test_health_check_no_auth_required(client: TestClient):
    """Test that health check doesn't require authentication."""
    response = client.get("/health")
    
    # Should succeed without authorization header
    assert response.status_code == 200


def test_readiness_check_with_db(client: TestClient):
    """Test readiness check endpoint."""
    response = client.get("/health/ready")
    
    # In tests, may not have Redis, so status may be 503
    # But we should at least get a response
    assert response.status_code in [200, 503]
    
    data = response.json()
    
    if response.status_code == 200:
        # Ready response has full details
        assert "status" in data
        assert data["status"] == "ready"
        assert "database" in data
        assert "redis" in data
        assert "timestamp" in data
    else:
        # 503 response has error detail
        assert "detail" in data


def test_root_endpoint(client: TestClient):
    """Test root endpoint returns API information."""
    response = client.get("/")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "operational"
