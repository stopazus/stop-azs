"""Persistence service using repository pattern."""

from datetime import datetime, timezone
from typing import Optional
import json
import structlog

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from api.models.database import SARRecord
from api.utils.telemetry import track_time, database_operations

logger = structlog.get_logger()


class SARRecordRepository:
    """Repository for SAR record persistence operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_idempotency_key(self, idempotency_key: str) -> Optional[SARRecord]:
        """
        Retrieve record by idempotency key.
        
        Args:
            idempotency_key: Unique idempotency key
            
        Returns:
            SARRecord if found, None otherwise
        """
        with track_time(database_operations, {"operation": "get_by_idempotency"}):
            return self.db.query(SARRecord).filter(
                SARRecord.idempotency_key == idempotency_key
            ).first()
    
    def create_record(
        self,
        request_id: str,
        submitter: str,
        sar_xml: str,
        normalized_payload: dict,
        content_hash: str,
        client_ip: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        validation_status: str = "valid",
        validation_errors: Optional[list] = None,
    ) -> SARRecord:
        """
        Create a new SAR record with transaction support.
        
        Args:
            request_id: Unique request correlation ID
            submitter: Identity of the submitter (from JWT subject)
            sar_xml: SAR XML representation
            normalized_payload: Normalized JSON payload
            content_hash: SHA256 hash of SAR XML
            client_ip: Client IP address (optional)
            idempotency_key: Idempotency key (optional)
            validation_status: Validation status (default: "valid")
            validation_errors: List of validation errors (optional)
            
        Returns:
            Created SARRecord instance
            
        Raises:
            IntegrityError: If idempotency key already exists
        """
        # Check idempotency
        if idempotency_key:
            existing = self.get_by_idempotency_key(idempotency_key)
            if existing:
                logger.info(
                    "idempotent_request_detected",
                    request_id=request_id,
                    existing_record_id=str(existing.id),
                    idempotency_key=idempotency_key
                )
                return existing
        
        # Serialize JSON fields to string for storage (SQLite compatibility)
        normalized_payload_json = json.dumps(normalized_payload)
        validation_errors_json = json.dumps(validation_errors) if validation_errors else None
        
        # Create new record
        record = SARRecord(
            request_id=request_id,
            submitter_identity=submitter,
            sar_xml=sar_xml,
            normalized_payload=normalized_payload_json,
            content_hash=content_hash,
            client_ip=client_ip,
            idempotency_key=idempotency_key,
            validation_status=validation_status,
            validation_errors=validation_errors_json,
            submitted_at=datetime.now(timezone.utc),
        )
        
        try:
            with track_time(database_operations, {"operation": "create"}):
                self.db.add(record)
                self.db.commit()
                self.db.refresh(record)
            
            logger.info(
                "sar_record_created",
                request_id=request_id,
                record_id=str(record.id),
                submitter=submitter,
            )
            
            return record
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(
                "database_integrity_error",
                request_id=request_id,
                error=str(e)
            )
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(
                "database_error",
                request_id=request_id,
                error=str(e),
                exc_info=True
            )
            raise
