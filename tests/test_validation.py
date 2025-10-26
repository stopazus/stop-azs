import textwrap
from datetime import date
from pathlib import Path

from stop_azs.validation import SarValidator


def write_tmp_file(tmp_path: Path, content: str, name: str = "sample.xml") -> Path:
    path = tmp_path / name
    path.write_text(textwrap.dedent(content).strip(), encoding="utf-8")
    return path


def test_malformed_xml(tmp_path: Path) -> None:
    path = write_tmp_file(
        tmp_path,
        """
        <SAR>
          <FilingInformation></FilingInformation>
        """,
    )
    validator = SarValidator(today=date(2024, 1, 1))
    issues = validator.validate_file(path)
    assert any(issue.code == "malformed_xml" for issue in issues)


def test_detects_placeholders_and_future_dates(tmp_path: Path) -> None:
    path = write_tmp_file(
        tmp_path,
        """
        <SAR xmlns="http://www.fincen.gov/base">
          <FilingInformation>
            <FilingDate>2025-09-11</FilingDate>
          </FilingInformation>
          <Transactions>
            <Transaction>
              <Date>2023-02-09</Date>
              <Amount currency="USD">PENDING</Amount>
              <UETR>PENDING</UETR>
            </Transaction>
          </Transactions>
        </SAR>
        """,
    )
    validator = SarValidator(today=date(2024, 1, 1))
    issues = validator.validate_file(path)

    codes = {issue.code for issue in issues}
    assert "future_filing_date" in codes
    assert "placeholder_amount" in codes
    assert "placeholder_uetr" in codes


def test_valid_amount_and_uetr(tmp_path: Path) -> None:
    path = write_tmp_file(
        tmp_path,
        """
        <SAR xmlns="http://www.fincen.gov/base">
          <FilingInformation>
            <FilingDate>2023-04-01</FilingDate>
          </FilingInformation>
          <Transactions>
            <Transaction>
              <Date>2023-02-09</Date>
              <Amount currency="USD">1024.55</Amount>
              <UETR>123E4567-E89B-12D3-A456-426614174000</UETR>
            </Transaction>
          </Transactions>
        </SAR>
        """,
    )
    validator = SarValidator(today=date(2024, 1, 1))
    issues = validator.validate_file(path)
    assert issues == []


def test_missing_transactions_and_required_fields(tmp_path: Path) -> None:
    path = write_tmp_file(
        tmp_path,
        """
        <SAR xmlns="http://www.fincen.gov/base">
          <FilingInformation>
            <FilingDate>2023-04-01</FilingDate>
          </FilingInformation>
        </SAR>
        """,
    )

    validator = SarValidator(today=date(2024, 1, 1))
    issues = validator.validate_file(path)
    codes = {issue.code for issue in issues}
    assert "missing_transactions_section" in codes


def test_missing_transaction_entry_details(tmp_path: Path) -> None:
    path = write_tmp_file(
        tmp_path,
        """
        <SAR xmlns="http://www.fincen.gov/base">
          <FilingInformation>
            <FilingDate>2023-04-01</FilingDate>
          </FilingInformation>
          <Transactions>
            <Transaction>
              <Amount currency="USD">100.00</Amount>
            </Transaction>
          </Transactions>
        </SAR>
        """,
    )

    validator = SarValidator(today=date(2024, 1, 1))
    issues = validator.validate_file(path)
    codes = {issue.code for issue in issues}
    assert "missing_transaction_date" in codes
    assert "missing_uetr_element" in codes


def test_duplicate_uetr_detection(tmp_path: Path) -> None:
    path = write_tmp_file(
        tmp_path,
        """
        <SAR xmlns="http://www.fincen.gov/base">
          <FilingInformation>
            <FilingDate>2023-04-01</FilingDate>
          </FilingInformation>
          <Transactions>
            <Transaction>
              <Date>2023-02-01</Date>
              <Amount currency="USD">100.00</Amount>
              <UETR>123E4567-E89B-12D3-A456-426614174000</UETR>
            </Transaction>
            <Transaction>
              <Date>2023-02-03</Date>
              <Amount currency="USD">50.00</Amount>
              <UETR>123e4567-e89b-12d3-a456-426614174000</UETR>
            </Transaction>
          </Transactions>
        </SAR>
        """,
    )

    validator = SarValidator(today=date(2024, 1, 1))
    issues = validator.validate_file(path)
    codes = {issue.code for issue in issues}
    assert "duplicate_uetr" in codes


def test_empty_file(tmp_path: Path) -> None:
    empty_path = write_tmp_file(tmp_path, "", name="empty.xml")
    validator = SarValidator(today=date(2024, 1, 1))
    issues = validator.validate_file(empty_path)
    codes = {issue.code for issue in issues}
    assert "empty_file" in codes


def test_icloud_placeholder_file(tmp_path: Path) -> None:
    placeholder_path = tmp_path / "pending.xml.icloud"
    placeholder_path.write_text("placeholder", encoding="utf-8")

    validator = SarValidator(today=date(2024, 1, 1))
    issues = validator.validate_file(placeholder_path)
    codes = {issue.code for issue in issues}
    assert "icloud_placeholder" in codes


def test_invalid_encoding_file(tmp_path: Path) -> None:
    binary_path = tmp_path / "binary.xml"
    binary_path.write_bytes(b"\xff\xfe\x00\x00")

    validator = SarValidator(today=date(2024, 1, 1))
    issues = validator.validate_file(binary_path)
    codes = {issue.code for issue in issues}
    assert "invalid_encoding" in codes
