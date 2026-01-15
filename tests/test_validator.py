import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sar_parser import validate_file, validate_string


VALID_SAR_XML = """\
<SAR>
  <FilingInformation>
    <FilingType>Initial</FilingType>
    <FilingDate>2024-05-01</FilingDate>
    <AmendmentType>None</AmendmentType>
  </FilingInformation>
  <FilerInformation>
    <FilerName>Example Financial</FilerName>
    <FilerAddress>
      <AddressLine1>123 Main St</AddressLine1>
      <City>New York</City>
      <State>NY</State>
      <ZIP>10001</ZIP>
      <Country>US</Country>
    </FilerAddress>
  </FilerInformation>
  <Subjects>
    <Subject>
      <Name>John Doe</Name>
      <EntityType>Individual</EntityType>
    </Subject>
  </Subjects>
  <Transactions>
    <Transaction>
      <Date>2024-04-30</Date>
      <Amount currency="USD">1000.50</Amount>
      <OriginatingAccount>
        <Name>Main Account</Name>
      </OriginatingAccount>
      <Beneficiaries>
        <Beneficiary>Jane Smith</Beneficiary>
      </Beneficiaries>
      <UETR>1234567890abcdef1234567890ABCDEF</UETR>
    </Transaction>
  </Transactions>
</SAR>
"""


class ValidateStringTests(unittest.TestCase):
    def test_valid_document(self) -> None:
        result = validate_string(VALID_SAR_XML)
        self.assertTrue(result.is_valid, result.errors)

    def test_reports_missing_sections(self) -> None:
        broken_xml = "<SAR><FilingInformation /></SAR>"
        result = validate_string(broken_xml)
        self.assertFalse(result.is_valid)
        error_messages = {error.message for error in result.errors}
        self.assertIn("Missing <FilerInformation> block.", error_messages)
        self.assertIn("At least one <Subject> is required.", error_messages)
        self.assertIn("At least one <Transaction> is required.", error_messages)

    def test_detects_placeholder_amount(self) -> None:
        xml = VALID_SAR_XML.replace("1000.50", "UNKNOWN")
        result = validate_string(xml)
        self.assertFalse(result.is_valid)
        self.assertIn(
            "Amount must be provided instead of a placeholder.",
            {error.message for error in result.errors},
        )

    def test_rejects_currency_symbols_and_commas(self) -> None:
        xml = VALID_SAR_XML.replace("1000.50", "$1,000.50")
        result = validate_string(xml)
        self.assertFalse(result.is_valid)
        self.assertIn(
            "Amount must not contain currency symbols or commas.",
            {error.message for error in result.errors},
        )

    def test_reports_missing_amount_location(self) -> None:
        xml = VALID_SAR_XML.replace(
            "      <Amount currency=\"USD\">1000.50</Amount>\n", ""
        )
        result = validate_string(xml)

        self.assertFalse(result.is_valid)
        self.assertEqual(
            (
                "Transaction is missing an <Amount> element.",
                "/SAR/Transactions/Transaction[1]/Amount",
            ),
            (result.errors[0].message, result.errors[0].location),
        )

    def test_rejects_non_numeric_amount(self) -> None:
        xml = VALID_SAR_XML.replace("1000.50", "one thousand")
        result = validate_string(xml)
        self.assertFalse(result.is_valid)
        self.assertIn(
            "Amount must be a valid numeric value.",
            {error.message for error in result.errors},
        )

    def test_rejects_negative_amount(self) -> None:
        xml = VALID_SAR_XML.replace("1000.50", "-10.00")
        result = validate_string(xml)
        self.assertFalse(result.is_valid)
        self.assertIn(
            "Amount must be a non-negative value.",
            {error.message for error in result.errors},
        )

    def test_rejects_excess_decimal_places(self) -> None:
        xml = VALID_SAR_XML.replace("1000.50", "10.123")
        result = validate_string(xml)
        self.assertFalse(result.is_valid)
        self.assertIn(
            "Amount cannot have more than 2 decimal places.",
            {error.message for error in result.errors},
        )

    def test_requires_uetr(self) -> None:
        xml = VALID_SAR_XML.replace("<UETR>1234567890abcdef1234567890ABCDEF</UETR>", "")
        result = validate_string(xml)
        self.assertFalse(result.is_valid)
        self.assertIn(
            "Transaction is missing a valid <UETR> identifier.",
            {error.message for error in result.errors},
        )

    def test_rejects_invalid_uetr_format(self) -> None:
        xml = VALID_SAR_XML.replace(
            "1234567890abcdef1234567890ABCDEF", "1234-invalid-uetr"
        )
        result = validate_string(xml)
        self.assertFalse(result.is_valid)
        self.assertIn(
            "UETR must be a valid 32-character hex string or UUID.",
            {error.message for error in result.errors},
        )

    def test_allows_standard_uuid_notation(self) -> None:
        xml = VALID_SAR_XML.replace(
            "1234567890abcdef1234567890ABCDEF",
            "12345678-90ab-cdef-1234-567890abcdef",
        )
        result = validate_string(xml)
        self.assertTrue(result.is_valid, result.errors)


class ValidateFileTests(unittest.TestCase):
    def test_reads_from_disk(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sar.xml"
            path.write_text(VALID_SAR_XML, encoding="utf-8")
            result = validate_file(path)
        self.assertTrue(result.is_valid, result.errors)


if __name__ == "__main__":
    unittest.main()
