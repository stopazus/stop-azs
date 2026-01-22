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

    def test_requires_filing_block(self) -> None:
        xml = """<SAR><Subjects /><Transactions /></SAR>"""
        result = validate_string(xml)
        self.assertFalse(result.is_valid)
        self.assertIn(
            "Missing <FilingInformation> block.",
            {error.message for error in result.errors},
        )

    def test_detects_placeholder_amount(self) -> None:
        xml = VALID_SAR_XML.replace("1000.50", "UNKNOWN")
        result = validate_string(xml)
        self.assertFalse(result.is_valid)
        self.assertIn(
            "Amount must be provided instead of a placeholder.",
            {error.message for error in result.errors},
        )

    def test_requires_transaction_date(self) -> None:
        xml = VALID_SAR_XML.replace("<Date>2024-04-30</Date>", "<Date>UNKNOWN</Date>")
        result = validate_string(xml)
        self.assertFalse(result.is_valid)
        self.assertIn(
            "Transaction date cannot be empty or a placeholder.",
            {error.message for error in result.errors},
        )

    def test_validates_uetr_format(self) -> None:
        xml = VALID_SAR_XML.replace(
            "1234567890abcdef1234567890ABCDEF",
            "1234-invalid-uetr-0000000000000",
        )
        result = validate_string(xml)
        self.assertFalse(result.is_valid)
        self.assertIn(
            "UETR must be a 32-character hexadecimal string.",
            {error.message for error in result.errors},
        )

    def test_requires_filer_address_details(self) -> None:
        xml = VALID_SAR_XML.replace(
            "<AddressLine1>123 Main St</AddressLine1>", "<AddressLine1></AddressLine1>"
        )
        xml = xml.replace("<City>New York</City>", "<City>UNKNOWN</City>")
        result = validate_string(xml)
        self.assertFalse(result.is_valid)
        error_messages = {error.message for error in result.errors}
        self.assertIn(
            "<AddressLine1> in filer address cannot be empty or a placeholder.",
            error_messages,
        )
        self.assertIn(
            "<City> in filer address cannot be empty or a placeholder.",
            error_messages,
        )

    def test_requires_amount_currency_code(self) -> None:
        xml = VALID_SAR_XML.replace(' currency="USD"', "")
        result = validate_string(xml)
        self.assertFalse(result.is_valid)
        self.assertIn(
            "Amount currency code is required.",
            {error.message for error in result.errors},
        )


class ValidateFileTests(unittest.TestCase):
    def test_reads_from_disk(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sar.xml"
            path.write_text(VALID_SAR_XML, encoding="utf-8")
            result = validate_file(path)
        self.assertTrue(result.is_valid, result.errors)

    def test_gracefully_handles_missing_file(self) -> None:
        missing_path = Path("F:/nonexistent/sar.xml")
        result = validate_file(missing_path)
        self.assertFalse(result.is_valid)
        self.assertTrue(
            any(
                error.message.startswith("Unable to read file 'F:/nonexistent/sar.xml'")
                for error in result.errors
            )
        )

    def test_provides_nas_drive_hint(self) -> None:
        missing_path = Path("G:/shared/sar.xml")
        result = validate_file(missing_path)
        self.assertFalse(result.is_valid)
        self.assertTrue(
            any(
                r"Drive G: is mapped to '\\\\nas\\Cloud-GDrive' (Google Drive)."
                in error.message
                for error in result.errors
            )
        )


if __name__ == "__main__":
    unittest.main()
