"""Request normalization service."""

from typing import Dict, Any, Tuple
import structlog

from api.models.schemas import SARSubmissionRequest

logger = structlog.get_logger()


def normalize_sar_request(request: SARSubmissionRequest) -> Tuple[str, Dict[str, Any]]:
    """
    Convert Pydantic model to internal SAR XML format.
    
    Args:
        request: Validated SAR submission request
        
    Returns:
        Tuple of (SAR XML string, normalized payload dict)
    """
    # Build SAR XML from request data
    xml_parts = ['<SAR>']
    
    # Filing Information
    xml_parts.append('  <FilingInformation>')
    xml_parts.append(f'    <FilingType>{_escape_xml(request.filing_type)}</FilingType>')
    xml_parts.append(f'    <FilingDate>{request.filing_date.isoformat()}</FilingDate>')
    xml_parts.append('    <AmendmentType>None</AmendmentType>')
    xml_parts.append('  </FilingInformation>')
    
    # Filer Information
    xml_parts.append('  <FilerInformation>')
    xml_parts.append(f'    <FilerName>{_escape_xml(request.filer_name)}</FilerName>')
    xml_parts.append('    <FilerAddress>')
    for key, value in request.filer_address.items():
        tag_name = _to_pascal_case(key)
        xml_parts.append(f'      <{tag_name}>{_escape_xml(value)}</{tag_name}>')
    xml_parts.append('    </FilerAddress>')
    xml_parts.append('  </FilerInformation>')
    
    # Subjects
    xml_parts.append('  <Subjects>')
    for subject in request.subjects:
        xml_parts.append('    <Subject>')
        for key, value in subject.items():
            tag_name = _to_pascal_case(key)
            xml_parts.append(f'      <{tag_name}>{_escape_xml(str(value))}</{tag_name}>')
        xml_parts.append('    </Subject>')
    xml_parts.append('  </Subjects>')
    
    # Transactions
    xml_parts.append('  <Transactions>')
    for transaction in request.transactions:
        xml_parts.append('    <Transaction>')
        for key, value in transaction.items():
            tag_name = _to_pascal_case(key)
            if key == 'amount':
                # Handle amount with currency attribute
                currency = transaction.get('currency', 'USD')
                xml_parts.append(f'      <Amount currency="{currency}">{_escape_xml(str(value))}</Amount>')
            elif key != 'currency':  # Skip currency as it's an attribute
                xml_parts.append(f'      <{tag_name}>{_escape_xml(str(value))}</{tag_name}>')
        xml_parts.append('    </Transaction>')
    xml_parts.append('  </Transactions>')
    
    xml_parts.append('</SAR>')
    
    sar_xml = '\n'.join(xml_parts)
    
    # Create normalized payload (JSON representation)
    normalized_payload = {
        "filing_type": request.filing_type.strip(),
        "filing_date": request.filing_date.isoformat(),
        "filer_name": request.filer_name.strip(),
        "filer_address": {k: v.strip() for k, v in request.filer_address.items()},
        "subjects": request.subjects,
        "transactions": request.transactions,
    }
    
    logger.debug(
        "request_normalized",
        subject_count=len(request.subjects),
        transaction_count=len(request.transactions)
    )
    
    return sar_xml, normalized_payload


def _escape_xml(text: str) -> str:
    """Escape XML special characters."""
    if not isinstance(text, str):
        text = str(text)
    return (text
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
        .replace("'", '&apos;')
        .strip())


def _to_pascal_case(snake_str: str) -> str:
    """Convert snake_case to PascalCase."""
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)
