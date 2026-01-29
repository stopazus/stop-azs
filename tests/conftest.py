"""Test configuration and fixtures."""

import sys
import os
from pathlib import Path

# Add project root to path - do this before any other imports
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(str(ROOT))

# Set test environment variable to disable Redis
os.environ['REDIS_URL'] = 'redis://fake-redis-for-tests:6379/0'

import pytest
import jwt
from datetime import datetime, timedelta, timezone
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from api.main import app, get_db
from api.models.database import Base
from api.config import settings


# Use in-memory SQLite for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a test database session."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database dependency override."""
    
    # Import here to ensure get_db is defined
    from api.main import app, get_db
    
    # Override database dependency
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
def valid_jwt_token() -> str:
    """Generate a valid JWT token with sar:write scope."""
    payload = {
        "sub": "test-user@example.com",
        "scope": "sar:write",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


@pytest.fixture
def expired_jwt_token() -> str:
    """Generate an expired JWT token."""
    payload = {
        "sub": "test-user@example.com",
        "scope": "sar:write",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        "iat": datetime.now(timezone.utc) - timedelta(hours=2)
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


@pytest.fixture
def insufficient_scope_token() -> str:
    """Generate a JWT token without required scope."""
    payload = {
        "sub": "test-user@example.com",
        "scope": "read:only",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


@pytest.fixture
def valid_sar_payload() -> dict:
    """Valid SAR submission payload."""
    return {
        "filing_type": "Initial",
        "filing_date": "2024-05-01",
        "filer_name": "Example Financial Institution",
        "filer_address": {
            "address_line1": "123 Main Street",
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
        ]
    }


@pytest.fixture
def invalid_sar_payload_missing_subject() -> dict:
    """Invalid SAR payload - missing subjects."""
    return {
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
        "subjects": [],  # Empty - should fail validation
        "transactions": [
            {
                "date": "2024-04-30",
                "amount": "1000.50",
                "currency": "USD"
            }
        ]
    }


@pytest.fixture
def invalid_sar_payload_placeholder_amount() -> dict:
    """Invalid SAR payload - placeholder amount."""
    return {
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
                "amount": "UNKNOWN",  # Placeholder - should fail validation
                "currency": "USD"
            }
        ]
    }
