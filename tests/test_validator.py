import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sar_parser import LiveUpdateMonitor, validate_file, validate_string


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


class ValidateFileTests(unittest.TestCase):
    def test_reads_from_disk(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sar.xml"
            path.write_text(VALID_SAR_XML, encoding="utf-8")
            result = validate_file(path)
        self.assertTrue(result.is_valid, result.errors)


class LiveUpdateMonitorTests(unittest.TestCase):
    def test_emits_updates_when_file_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sar.xml"
            path.write_text(VALID_SAR_XML, encoding="utf-8")

            monitor = LiveUpdateMonitor(path)
            first = monitor.poll_once()
            self.assertIsNotNone(first)
            assert first is not None
            self.assertTrue(first.result.is_valid)

            self.assertIsNone(monitor.poll_once())

            path.write_text(VALID_SAR_XML.replace("1000.50", "UNKNOWN"), encoding="utf-8")
            second = monitor.poll_once()
            self.assertIsNotNone(second)
            assert second is not None
            self.assertFalse(second.result.is_valid)

    def test_run_requires_positive_interval(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sar.xml"
            path.write_text(VALID_SAR_XML, encoding="utf-8")
            monitor = LiveUpdateMonitor(path)

            iterator = monitor.run(interval=0)
            with self.assertRaises(ValueError):
                next(iterator)

    def test_missing_file_is_tolerated_until_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sar.xml"
            monitor = LiveUpdateMonitor(path)

            # First poll should quietly return None when the file is absent.
            self.assertIsNone(monitor.poll_once())

            # After writing the file we should see a validation result.
            path.write_text(VALID_SAR_XML, encoding="utf-8")
            update = monitor.poll_once()
            self.assertIsNotNone(update)
            assert update is not None
            self.assertTrue(update.result.is_valid)


if __name__ == "__main__":
    unittest.main()
