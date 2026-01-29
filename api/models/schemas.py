"""Pydantic schemas for request/response validation."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SARSubmissionRequest(BaseModel):
    """Request schema for SAR submission."""
    
    filing_type: str = Field(..., min_length=1, max_length=50)
    filing_date: date
    filer_name: str = Field(..., min_length=1, max_length=255)
    filer_address: Dict[str, str]
    subjects: List[Dict[str, Any]] = Field(..., min_items=1)
    transactions: List[Dict[str, Any]] = Field(..., min_items=1)
    
    # Optional idempotency
    idempotency_key: Optional[str] = Field(None, max_length=128)
    
    @field_validator('subjects')
    @classmethod
    def validate_subjects(cls, v):
        if not v:
            raise ValueError("At least one subject is required")
        return v
    
    @field_validator('transactions')
    @classmethod
    def validate_transactions(cls, v):
        if not v:
            raise ValueError("At least one transaction is required")
        return v
    
    model_config = {
        "extra": "forbid",  # Drop any fields not defined
        "json_schema_extra": {
            "example": {
                "filing_type": "Initial",
                "filing_date": "2024-05-01",
                "filer_name": "Example Financial",
                "filer_address": {
                    "address_line1": "123 Main St",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10001",
                    "country": "US"
                },
                "subjects": [
                    {
                        "name": "John Doe",
                        "entity_type": "Individual"
                    }
                ],
                "transactions": [
                    {
                        "date": "2024-04-30",
                        "amount": "1000.50",
                        "currency": "USD"
                    }
                ],
                "idempotency_key": "unique-key-123"
            }
        }
    }


class SARSubmissionResponse(BaseModel):
    """Response schema for successful SAR submission."""
    
    record_id: UUID
    request_id: str
    submitted_at: datetime
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "record_id": "550e8400-e29b-41d4-a716-446655440000",
                "request_id": "req_abc123xyz",
                "submitted_at": "2024-05-01T12:34:56.789Z"
            }
        }
    }


class ValidationErrorDetail(BaseModel):
    """Detail for a single validation error."""
    
    message: str
    location: Optional[str] = None
    severity: str = "error"


class ValidationErrorResponse(BaseModel):
    """Response schema for validation errors."""
    
    detail: str = "Validation failed"
    errors: List[ValidationErrorDetail]
    request_id: str


class HealthResponse(BaseModel):
    """Response schema for health check."""
    
    status: str
    timestamp: datetime
    version: str


class ReadinessResponse(BaseModel):
    """Response schema for readiness check."""
    
    status: str
    timestamp: datetime
    database: str
    redis: str
