"""SAR submission endpoint."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
import structlog

from api.middleware.auth import verify_token, get_submitter_identity
from api.middleware.logging import get_request_id
from api.models.schemas import (
    SARSubmissionRequest,
    SARSubmissionResponse,
    ValidationErrorResponse,
)
from api.services.normalization import normalize_sar_request
from api.services.validation import validate_sar_xml
from api.services.persistence import SARRecordRepository
from api.utils.hash import compute_content_hash
from api.utils.telemetry import (
    sar_submissions_total,
    sar_submission_duration,
    validation_errors_total,
    active_requests,
    track_time,
)

logger = structlog.get_logger()
router = APIRouter(prefix="/api", tags=["SAR Records"])


# Database session dependency (will be properly set in main.py)
def get_db():
    """Placeholder for database session dependency."""
    pass


@router.post(
    "/sar-records",
    response_model=SARSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "SAR record created successfully"},
        401: {"description": "Invalid or missing authentication token"},
        403: {"description": "Insufficient permissions"},
        422: {"description": "Validation failed"},
        503: {"description": "Service unavailable"},
    }
)
async def submit_sar_record(
    request: Request,
    sar_request: SARSubmissionRequest,
    token_payload: dict = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """
    Submit a new SAR record.
    
    This endpoint implements the complete 9-step flow documented in
    docs/request_flow.md:
    
    1. Client request (this endpoint)
    2. Edge protections (nginx/rate limiting)
    3. Authentication & authorization (JWT bearer token)
    4. Request normalization (JSON → SAR XML)
    5. Business validation (sar_parser.validator)
    6. Persistence preparation (timestamps, hashing)
    7. Database transaction (PostgreSQL)
    8. Audit & telemetry (structured logging)
    9. Response (201 Created or error)
    
    Args:
        request: FastAPI request object
        sar_request: SAR submission data
        token_payload: Validated JWT token payload
        db: Database session
        
    Returns:
        SARSubmissionResponse with record ID and request ID
        
    Raises:
        HTTPException: For validation errors or service unavailability
    """
    # Track active requests
    active_requests.inc()
    
    try:
        # Get request metadata
        request_id = get_request_id(request)
        submitter = get_submitter_identity(token_payload)
        client_ip = request.client.host if request.client else None
        
        # Start tracking submission duration
        with track_time(sar_submission_duration):
            
            # Step 1: Log submission received
            logger.info(
                "sar_submission_received",
                request_id=request_id,
                submitter=submitter,
                client_ip=client_ip,
                idempotency_key=sar_request.idempotency_key
            )
            
            # Step 2: Normalize request (convert to SAR XML)
            sar_xml, normalized_payload = normalize_sar_request(sar_request)
            
            # Step 3: Validate SAR XML
            is_valid, validation_errors = validate_sar_xml(sar_xml, request_id)
            
            if not is_valid:
                # Track validation failure
                sar_submissions_total.labels(status="validation_failed").inc()
                validation_errors_total.inc()
                
                # Return 422 with structured errors
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=ValidationErrorResponse(
                        detail="Validation failed",
                        errors=validation_errors,
                        request_id=request_id
                    ).model_dump()
                )
            
            # Step 4: Compute content hash
            content_hash = compute_content_hash(sar_xml)
            
            # Step 5: Persist to database
            try:
                repository = SARRecordRepository(db)
                record = repository.create_record(
                    request_id=request_id,
                    submitter=submitter,
                    sar_xml=sar_xml,
                    normalized_payload=normalized_payload,
                    content_hash=content_hash,
                    client_ip=client_ip,
                    idempotency_key=sar_request.idempotency_key,
                )
                
                # Track success
                sar_submissions_total.labels(status="success").inc()
                
                # Return success response
                return SARSubmissionResponse(
                    record_id=record.id,
                    request_id=request_id,
                    submitted_at=record.submitted_at
                )
                
            except Exception as e:
                # Track database error
                sar_submissions_total.labels(status="database_error").inc()
                
                logger.error(
                    "database_transaction_failed",
                    request_id=request_id,
                    error=str(e),
                    exc_info=True
                )
                
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Service temporarily unavailable"
                )
    
    finally:
        # Decrement active requests counter
        active_requests.dec()
