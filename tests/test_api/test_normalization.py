"""Tests for normalization service."""

import pytest
from datetime import date
from api.models.schemas import SARSubmissionRequest
from api.services.normalization import normalize_sar_request


def test_normalize_valid_request():
    """Test normalization of a valid SAR request."""
    request = SARSubmissionRequest(
        filing_type="Initial",
        filing_date=date(2024, 5, 1),
        filer_name="Example Financial",
        filer_address={
            "address_line1": "123 Main St",
            "city": "New York",
            "state": "NY",
            "zip": "10001",
            "country": "US"
        },
        subjects=[
            {
                "name": "John Doe",
                "entity_type": "Individual"
            }
        ],
        transactions=[
            {
                "date": "2024-04-30",
                "amount": "1000.50",
                "currency": "USD"
            }
        ]
    )
    
    sar_xml, normalized_payload = normalize_sar_request(request)
    
    # Check XML is generated
    assert "<SAR>" in sar_xml
    assert "</SAR>" in sar_xml
    assert "<FilerInformation>" in sar_xml
    assert "<FilingType>Initial</FilingType>" in sar_xml
    assert "<FilerName>Example Financial</FilerName>" in sar_xml
    
    # Check normalized payload
    assert normalized_payload["filing_type"] == "Initial"
    assert normalized_payload["filing_date"] == "2024-05-01"
    assert normalized_payload["filer_name"] == "Example Financial"


def test_normalize_request_strips_whitespace():
    """Test that normalization strips whitespace from strings."""
    request = SARSubmissionRequest(
        filing_type="  Initial  ",
        filing_date=date(2024, 5, 1),
        filer_name="  Example Financial  ",
        filer_address={
            "address_line1": "  123 Main St  ",
            "city": "  New York  ",
            "state": "NY",
            "zip": "10001",
            "country": "US"
        },
        subjects=[
            {
                "name": "John Doe",
                "entity_type": "Individual"
            }
        ],
        transactions=[
            {
                "date": "2024-04-30",
                "amount": "1000.50",
                "currency": "USD"
            }
        ]
    )
    
    sar_xml, normalized_payload = normalize_sar_request(request)
    
    # Check whitespace is stripped
    assert normalized_payload["filing_type"] == "Initial"
    assert normalized_payload["filer_name"] == "Example Financial"
    assert normalized_payload["filer_address"]["address_line1"] == "123 Main St"
    assert normalized_payload["filer_address"]["city"] == "New York"


def test_normalize_request_escapes_xml_characters():
    """Test that XML special characters are escaped."""
    request = SARSubmissionRequest(
        filing_type="Initial",
        filing_date=date(2024, 5, 1),
        filer_name="Example & Associates <Test>",
        filer_address={
            "address_line1": "123 Main St",
            "city": "New York",
            "state": "NY",
            "zip": "10001",
            "country": "US"
        },
        subjects=[
            {
                "name": "John Doe",
                "entity_type": "Individual"
            }
        ],
        transactions=[
            {
                "date": "2024-04-30",
                "amount": "1000.50",
                "currency": "USD"
            }
        ]
    )
    
    sar_xml, normalized_payload = normalize_sar_request(request)
    
    # Check XML escaping
    assert "&amp;" in sar_xml
    assert "&lt;" in sar_xml
    assert "&gt;" in sar_xml
    # Raw characters should not appear
    assert "<Test>" not in sar_xml or sar_xml.count("<Test>") == 0  # Only in tags


def test_normalize_converts_snake_case_to_pascal_case():
    """Test that snake_case fields are converted to PascalCase in XML."""
    request = SARSubmissionRequest(
        filing_type="Initial",
        filing_date=date(2024, 5, 1),
        filer_name="Example Financial",
        filer_address={
            "address_line1": "123 Main St",
            "address_line2": "Suite 100",
            "city": "New York",
            "state": "NY",
            "zip": "10001",
            "country": "US"
        },
        subjects=[
            {
                "name": "John Doe",
                "entity_type": "Individual"
            }
        ],
        transactions=[
            {
                "date": "2024-04-30",
                "amount": "1000.50",
                "currency": "USD"
            }
        ]
    )
    
    sar_xml, normalized_payload = normalize_sar_request(request)
    
    # Check PascalCase tags
    assert "<AddressLine1>" in sar_xml
    assert "<AddressLine2>" in sar_xml


def test_normalize_handles_amount_with_currency():
    """Test that amount is normalized with currency attribute."""
    request = SARSubmissionRequest(
        filing_type="Initial",
        filing_date=date(2024, 5, 1),
        filer_name="Example Financial",
        filer_address={
            "address_line1": "123 Main St",
            "city": "New York",
            "state": "NY",
            "zip": "10001",
            "country": "US"
        },
        subjects=[
            {
                "name": "John Doe",
                "entity_type": "Individual"
            }
        ],
        transactions=[
            {
                "date": "2024-04-30",
                "amount": "1000.50",
                "currency": "EUR"
            }
        ]
    )
    
    sar_xml, normalized_payload = normalize_sar_request(request)
    
    # Check currency attribute
    assert 'currency="EUR"' in sar_xml
    assert "<Amount" in sar_xml
