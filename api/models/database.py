"""SQLAlchemy database models for SAR records."""

from datetime import datetime
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

Base = declarative_base()


class SARRecord(Base):
    """SAR submission record stored in PostgreSQL."""
    
    __tablename__ = "sar_records"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    
    # Request metadata
    request_id = Column(String(64), nullable=False, unique=True, index=True)
    submitter_identity = Column(String(255), nullable=False, index=True)
    submitted_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    client_ip = Column(INET, nullable=True)
    
    # SAR content
    sar_xml = Column(Text, nullable=False)
    normalized_payload = Column(JSONB, nullable=False)
    
    # Evidence & audit
    content_hash = Column(String(64), nullable=False)
    idempotency_key = Column(String(128), unique=True, nullable=True)
    
    # Validation metadata
    validation_status = Column(String(20), nullable=False, default="valid")
    validation_errors = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    
    __table_args__ = (
        Index("idx_sar_records_submitted_at", "submitted_at"),
        Index("idx_sar_records_submitter", "submitter_identity"),
        Index(
            "idx_sar_records_idempotency",
            "idempotency_key",
            postgresql_where=text("idempotency_key IS NOT NULL")
        ),
    )
    
    def __repr__(self) -> str:
        return f"<SARRecord(id={self.id}, request_id={self.request_id})>"
