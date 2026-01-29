"""Tests for idempotency handling."""

import pytest
from fastapi.testclient import TestClient


def test_duplicate_idempotency_key_returns_same_record(
    client: TestClient,
    valid_jwt_token: str,
    valid_sar_payload: dict
):
    """Test that duplicate idempotency key returns the same record."""
    payload = valid_sar_payload.copy()
    payload["idempotency_key"] = "idempotency-test-key-1"
    
    # First submission
    response1 = client.post(
        "/api/sar-records",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json=payload
    )
    
    assert response1.status_code == 201
    data1 = response1.json()
    record_id_1 = data1["record_id"]
    
    # Second submission with same key
    response2 = client.post(
        "/api/sar-records",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json=payload
    )
    
    assert response2.status_code == 201
    data2 = response2.json()
    record_id_2 = data2["record_id"]
    
    # Should be the same record
    assert record_id_1 == record_id_2


def test_different_idempotency_keys_create_different_records(
    client: TestClient,
    valid_jwt_token: str,
    valid_sar_payload: dict
):
    """Test that different idempotency keys create different records."""
    payload1 = valid_sar_payload.copy()
    payload1["idempotency_key"] = "idempotency-key-1"
    
    payload2 = valid_sar_payload.copy()
    payload2["idempotency_key"] = "idempotency-key-2"
    
    # First submission
    response1 = client.post(
        "/api/sar-records",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json=payload1
    )
    
    assert response1.status_code == 201
    record_id_1 = response1.json()["record_id"]
    
    # Second submission with different key
    response2 = client.post(
        "/api/sar-records",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json=payload2
    )
    
    assert response2.status_code == 201
    record_id_2 = response2.json()["record_id"]
    
    # Should be different records
    assert record_id_1 != record_id_2


def test_no_idempotency_key_creates_new_records(
    client: TestClient,
    valid_jwt_token: str,
    valid_sar_payload: dict
):
    """Test that without idempotency key, each submission creates a new record."""
    # First submission
    response1 = client.post(
        "/api/sar-records",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json=valid_sar_payload
    )
    
    assert response1.status_code == 201
    record_id_1 = response1.json()["record_id"]
    
    # Second submission (no idempotency key)
    response2 = client.post(
        "/api/sar-records",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json=valid_sar_payload
    )
    
    assert response2.status_code == 201
    record_id_2 = response2.json()["record_id"]
    
    # Should be different records
    assert record_id_1 != record_id_2


def test_idempotency_with_different_payloads(
    client: TestClient,
    valid_jwt_token: str,
    valid_sar_payload: dict
):
    """Test idempotency with same key but different payloads."""
    idempotency_key = "same-idempotency-key"
    
    # First submission
    payload1 = valid_sar_payload.copy()
    payload1["idempotency_key"] = idempotency_key
    payload1["filer_name"] = "First Filer"
    
    response1 = client.post(
        "/api/sar-records",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json=payload1
    )
    
    assert response1.status_code == 201
    record_id_1 = response1.json()["record_id"]
    
    # Second submission with same key but different payload
    payload2 = valid_sar_payload.copy()
    payload2["idempotency_key"] = idempotency_key
    payload2["filer_name"] = "Second Filer"
    
    response2 = client.post(
        "/api/sar-records",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json=payload2
    )
    
    assert response2.status_code == 201
    record_id_2 = response2.json()["record_id"]
    
    # Should return the original record (idempotency enforced)
    assert record_id_1 == record_id_2
