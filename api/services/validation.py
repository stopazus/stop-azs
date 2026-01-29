"""SAR validation service integrating with sar_parser."""

from typing import List
import structlog

from sar_parser import validate_string, ValidationResult
from api.models.schemas import ValidationErrorDetail

logger = structlog.get_logger()


def validate_sar_xml(sar_xml: str, request_id: str) -> tuple[bool, List[ValidationErrorDetail]]:
    """
    Validate SAR XML using the existing sar_parser validator.
    
    Args:
        sar_xml: SAR XML string to validate
        request_id: Request correlation ID for logging
        
    Returns:
        Tuple of (is_valid, list of validation errors)
    """
    # Call existing validator
    result: ValidationResult = validate_string(sar_xml)
    
    if not result.is_valid:
        # Convert ValidationError objects to ValidationErrorDetail
        error_details = [
            ValidationErrorDetail(
                message=error.message,
                location=error.location,
                severity=error.severity
            )
            for error in result.errors
        ]
        
        logger.warning(
            "sar_validation_failed",
            request_id=request_id,
            error_count=len(error_details),
            errors=[e.message for e in result.errors[:5]]  # First 5 errors
        )
        
        return False, error_details
    
    logger.info(
        "sar_validation_passed",
        request_id=request_id
    )
    
    return True, []
