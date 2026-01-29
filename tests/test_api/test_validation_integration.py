"""Tests for validation service integration with sar_parser."""

import pytest
from api.services.validation import validate_sar_xml


def test_validate_valid_sar_xml():
    """Test validation of a valid SAR XML."""
    sar_xml = """
    <SAR>
      <FilerInformation>
        <FilerName>Example Financial</FilerName>
      </FilerInformation>
      <Subjects>
        <Subject>
          <Name>John Doe</Name>
        </Subject>
      </Subjects>
      <Transactions>
        <Transaction>
          <Amount currency="USD">1000.50</Amount>
        </Transaction>
      </Transactions>
    </SAR>
    """
    
    is_valid, errors = validate_sar_xml(sar_xml, "test-request-id")
    
    assert is_valid is True
    assert len(errors) == 0


def test_validate_invalid_sar_missing_filer():
    """Test validation fails when FilerInformation is missing."""
    sar_xml = """
    <SAR>
      <Subjects>
        <Subject>
          <Name>John Doe</Name>
        </Subject>
      </Subjects>
      <Transactions>
        <Transaction>
          <Amount currency="USD">1000.50</Amount>
        </Transaction>
      </Transactions>
    </SAR>
    """
    
    is_valid, errors = validate_sar_xml(sar_xml, "test-request-id")
    
    assert is_valid is False
    assert len(errors) > 0
    
    error_messages = [e.message for e in errors]
    assert any("FilerInformation" in msg for msg in error_messages)


def test_validate_invalid_sar_missing_subjects():
    """Test validation fails when subjects are missing."""
    sar_xml = """
    <SAR>
      <FilerInformation>
        <FilerName>Example Financial</FilerName>
      </FilerInformation>
      <Transactions>
        <Transaction>
          <Amount currency="USD">1000.50</Amount>
        </Transaction>
      </Transactions>
    </SAR>
    """
    
    is_valid, errors = validate_sar_xml(sar_xml, "test-request-id")
    
    assert is_valid is False
    assert len(errors) > 0
    
    error_messages = [e.message for e in errors]
    assert any("Subject" in msg for msg in error_messages)


def test_validate_invalid_sar_placeholder_amount():
    """Test validation fails with placeholder amount."""
    sar_xml = """
    <SAR>
      <FilerInformation>
        <FilerName>Example Financial</FilerName>
      </FilerInformation>
      <Subjects>
        <Subject>
          <Name>John Doe</Name>
        </Subject>
      </Subjects>
      <Transactions>
        <Transaction>
          <Amount currency="USD">UNKNOWN</Amount>
        </Transaction>
      </Transactions>
    </SAR>
    """
    
    is_valid, errors = validate_sar_xml(sar_xml, "test-request-id")
    
    assert is_valid is False
    assert len(errors) > 0
    
    error_messages = [e.message for e in errors]
    assert any("placeholder" in msg.lower() for msg in error_messages)


def test_validation_errors_have_location():
    """Test that validation errors include location information."""
    sar_xml = """
    <SAR>
      <FilerInformation>
        <FilerName>Example Financial</FilerName>
      </FilerInformation>
      <Subjects>
        <Subject>
          <Name>John Doe</Name>
        </Subject>
      </Subjects>
      <Transactions>
        <Transaction>
          <Amount currency="USD">PENDING</Amount>
        </Transaction>
      </Transactions>
    </SAR>
    """
    
    is_valid, errors = validate_sar_xml(sar_xml, "test-request-id")
    
    assert is_valid is False
    assert len(errors) > 0
    
    # Errors should have location
    for error in errors:
        assert error.location is not None
        assert error.location.startswith("/SAR")
