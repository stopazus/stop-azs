import sys
from pathlib import Path

import pytest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sar_parser.validator import _validate_transactions, ValidationResult


# Helper to create a minimal valid transaction XML tree
def create_transaction_xml(uetr_value=None, missing_uetr_tag=False):
    root = ET.Element("Root")
    transactions = ET.SubElement(root, "Transactions")
    txn = ET.SubElement(transactions, "Transaction")

    # Amount is required to pass the first check in _validate_transactions
    amount = ET.SubElement(txn, "Amount")
    amount.text = "1000.00"

    if not missing_uetr_tag:
        uetr = ET.SubElement(txn, "UETR")
        if uetr_value is not None:
            uetr.text = uetr_value

    return root


class TestUETRValidation:
    def test_valid_uuid_with_hyphens(self):
        """Should accept a standard 36-char UUID with hyphens."""
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        root = create_transaction_xml(uetr_value=valid_uuid)
        result = ValidationResult()

        _validate_transactions(root, result)

        assert len(result.errors) == 0, f"Expected valid UUID to pass, got errors: {result.errors}"

    def test_valid_hex_string_no_hyphens(self):
        """Should accept a 32-char hex string (SWIFT/ISO raw format)."""
        valid_hex = "550e8400e29b41d4a716446655440000"
        root = create_transaction_xml(uetr_value=valid_hex)
        result = ValidationResult()

        _validate_transactions(root, result)

        assert len(result.errors) == 0, f"Expected valid hex string to pass, got errors: {result.errors}"

    def test_invalid_uuid_wrong_characters(self):
        """Should fail if string contains non-hex characters (e.g., 'Z')."""
        invalid_val = "ZZZe8400-e29b-41d4-a716-446655440000"
        root = create_transaction_xml(uetr_value=invalid_val)
        result = ValidationResult()

        _validate_transactions(root, result)

        assert len(result.errors) == 1
        assert "UETR must be a valid 32-character hex string or UUID" in result.errors[0].message

    def test_invalid_length(self):
        """Should fail if the string is too short or too long."""
        short_val = "550e8400"
        root = create_transaction_xml(uetr_value=short_val)
        result = ValidationResult()

        _validate_transactions(root, result)

        assert len(result.errors) == 1
        assert "UETR must be a valid 32-character hex string or UUID" in result.errors[0].message

    def test_missing_uetr_tag(self):
        """Should fail if the <UETR> tag is completely missing."""
        root = create_transaction_xml(missing_uetr_tag=True)
        result = ValidationResult()

        _validate_transactions(root, result)

        assert len(result.errors) == 1
        assert "Transaction is missing a valid <UETR> identifier" in result.errors[0].message

    def test_placeholder_uetr(self):
        """Should fail if the UETR is 'UNKNOWN' or empty."""
        root = create_transaction_xml(uetr_value="UNKNOWN")
        result = ValidationResult()

        _validate_transactions(root, result)

        assert len(result.errors) == 1
        assert "Transaction is missing a valid <UETR> identifier" in result.errors[0].message
