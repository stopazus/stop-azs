"""SQLAlchemy database models for SAR records."""

from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Index,
    TIMESTAMP,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator, CHAR

Base = declarative_base()


# UUID type that works with both PostgreSQL and SQLite
class GUID(TypeDecorator):
    """Platform-independent GUID type.
    
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            else:
                return str(uuid.UUID(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if isinstance(value, uuid.UUID):
                return value
            else:
                return uuid.UUID(value)


class SARRecord(Base):
    """SAR submission record stored in database.
    
    Note: Uses PostgreSQL for production. SQLite compatibility for tests only.
    """
    
    __tablename__ = "sar_records"
    
    # Primary key
    id = Column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Request metadata
    request_id = Column(String(64), nullable=False, unique=True, index=True)
    submitter_identity = Column(String(255), nullable=False, index=True)
    submitted_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    client_ip = Column(String(45), nullable=True)  # INET for PostgreSQL, String for SQLite
    
    # SAR content  
    sar_xml = Column(Text, nullable=False)
    normalized_payload = Column(Text, nullable=False)  # JSONB in PostgreSQL, Text in SQLite
    
    # Evidence & audit
    content_hash = Column(String(64), nullable=False)
    idempotency_key = Column(String(128), unique=True, nullable=True)
    
    # Validation metadata
    validation_status = Column(String(20), nullable=False, default="valid")
    validation_errors = Column(Text, nullable=True)  # JSONB in PostgreSQL, Text in SQLite
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    __table_args__ = (
        Index("idx_sar_records_submitted_at", "submitted_at"),
        Index("idx_sar_records_submitter", "submitter_identity"),
    )
    
    def __repr__(self) -> str:
        return f"<SARRecord(id={self.id}, request_id={self.request_id})>"
