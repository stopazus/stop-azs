"""Tests for SAR submission endpoint."""

import pytest
from fastapi.testclient import TestClient


def test_submit_valid_sar_returns_201(
    client: TestClient,
    valid_jwt_token: str,
    valid_sar_payload: dict
):
    """Test that a valid SAR submission returns 201 Created."""
    response = client.post(
        "/api/sar-records",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json=valid_sar_payload
    )
    
    assert response.status_code == 201
    
    data = response.json()
    assert "record_id" in data
    assert "request_id" in data
    assert "submitted_at" in data
    
    # Check response headers
    assert "X-Request-ID" in response.headers


def test_submit_sar_without_auth_returns_401_or_403(
    client: TestClient,
    valid_sar_payload: dict
):
    """Test that submission without auth returns 401 or 403."""
    response = client.post(
        "/api/sar-records",
        json=valid_sar_payload
    )
    
    # FastAPI HTTPBearer returns 403 for missing/invalid header format
    assert response.status_code in [401, 403]


def test_submit_invalid_sar_missing_subjects_returns_422(
    client: TestClient,
    valid_jwt_token: str,
    invalid_sar_payload_missing_subject: dict
):
    """Test that SAR with missing subjects returns 422."""
    response = client.post(
        "/api/sar-records",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json=invalid_sar_payload_missing_subject
    )
    
    # Pydantic validation should catch empty subjects
    assert response.status_code == 422


def test_submit_invalid_sar_placeholder_amount_returns_422(
    client: TestClient,
    valid_jwt_token: str,
    invalid_sar_payload_placeholder_amount: dict
):
    """Test that SAR with placeholder amount returns 422."""
    response = client.post(
        "/api/sar-records",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json=invalid_sar_payload_placeholder_amount
    )
    
    assert response.status_code == 422
    
    data = response.json()
    assert "detail" in data
    
    # Should contain validation errors
    if isinstance(data["detail"], dict):
        assert "errors" in data["detail"]
        errors = data["detail"]["errors"]
        # Check that placeholder error is mentioned
        error_messages = [e["message"] for e in errors]
        assert any("placeholder" in msg.lower() for msg in error_messages)


def test_submit_sar_with_idempotency_key(
    client: TestClient,
    valid_jwt_token: str,
    valid_sar_payload: dict
):
    """Test SAR submission with idempotency key."""
    payload = valid_sar_payload.copy()
    payload["idempotency_key"] = "test-idempotency-key-123"
    
    # First submission
    response1 = client.post(
        "/api/sar-records",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json=payload
    )
    
    assert response1.status_code == 201
    record_id_1 = response1.json()["record_id"]
    
    # Second submission with same idempotency key
    response2 = client.post(
        "/api/sar-records",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json=payload
    )
    
    assert response2.status_code == 201
    record_id_2 = response2.json()["record_id"]
    
    # Should return the same record
    assert record_id_1 == record_id_2


def test_submit_malformed_json_returns_422(
    client: TestClient,
    valid_jwt_token: str
):
    """Test that malformed JSON returns 422."""
    response = client.post(
        "/api/sar-records",
        headers={
            "Authorization": f"Bearer {valid_jwt_token}",
            "Content-Type": "application/json"
        },
        content="{invalid json"
    )
    
    assert response.status_code == 422


def test_submit_sar_with_extra_fields_forbidden(
    client: TestClient,
    valid_jwt_token: str,
    valid_sar_payload: dict
):
    """Test that extra fields are rejected (Pydantic extra='forbid')."""
    payload = valid_sar_payload.copy()
    payload["extra_field"] = "should be rejected"
    
    response = client.post(
        "/api/sar-records",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json=payload
    )
    
    # Should fail validation due to extra field
    assert response.status_code == 422


def test_submit_sar_missing_required_field_returns_422(
    client: TestClient,
    valid_jwt_token: str,
    valid_sar_payload: dict
):
    """Test that missing required field returns 422."""
    payload = valid_sar_payload.copy()
    del payload["filing_type"]  # Remove required field
    
    response = client.post(
        "/api/sar-records",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json=payload
    )
    
    assert response.status_code == 422


def test_request_id_in_response_headers(
    client: TestClient,
    valid_jwt_token: str,
    valid_sar_payload: dict
):
    """Test that X-Request-ID is present in response headers."""
    response = client.post(
        "/api/sar-records",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json=valid_sar_payload
    )
    
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"].startswith("req_")


def test_custom_request_id_is_preserved(
    client: TestClient,
    valid_jwt_token: str,
    valid_sar_payload: dict
):
    """Test that custom X-Request-ID is preserved."""
    custom_request_id = "custom-request-123"
    
    response = client.post(
        "/api/sar-records",
        headers={
            "Authorization": f"Bearer {valid_jwt_token}",
            "X-Request-ID": custom_request_id
        },
        json=valid_sar_payload
    )
    
    assert response.headers["X-Request-ID"] == custom_request_id
