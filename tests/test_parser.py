import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sar_parser import parse_sar


@pytest.fixture
def sample_xml(tmp_path: Path) -> Path:
    xml_content = """
    <SAR xmlns=
        "http://www.fincen.gov/base">
      <FilingInformation>
        <FilingType>Initial</FilingType>
        <FilingDate>2025-01-01</FilingDate>
        <AmendmentType>None</AmendmentType>
        <ContactOffice>Sample Office</ContactOffice>
        <ContactPhone>000-000-0000</ContactPhone>
        <ContactEmail>sar@example.com</ContactEmail>
      </FilingInformation>
      <FilerInformation>
        <FilerName>Example Filer</FilerName>
      </FilerInformation>
      <Subjects>
        <Subject>
          <EntityType>Business</EntityType>
          <Name>Example Subject</Name>
        </Subject>
        <Subject>
          <EntityType>Individual</EntityType>
          <Name>John Doe</Name>
        </Subject>
      </Subjects>
      <Transactions>
        <Transaction>
          <Date>2025-02-03</Date>
          <Amount currency="USD">1000.00</Amount>
          <OriginatingAccount>
            <Name>Example Origin</Name>
          </OriginatingAccount>
          <PassThroughAccounts>
            <Account>123</Account>
            <Account>456</Account>
          </PassThroughAccounts>
          <Beneficiaries>
            <Beneficiary>Alice</Beneficiary>
            <Beneficiary>Bob</Beneficiary>
          </Beneficiaries>
          <UETR>1234</UETR>
          <Notes>Sample notes</Notes>
        </Transaction>
      </Transactions>
    </SAR>
    """
    file_path = tmp_path / "sample.xml"
    file_path.write_text(xml_content, encoding="utf-8")
    return file_path


def test_parse_sar_extracts_core_fields(sample_xml: Path) -> None:
    content = sample_xml.read_text(encoding="utf-8")
    data = parse_sar(content)

    assert data.filing_type == "Initial"
    assert data.filing_date == "2025-01-01"
    assert data.contact_office == "Sample Office"
    assert data.filer_name == "Example Filer"

    assert len(data.subjects) == 2
    assert data.subjects[0].name == "Example Subject"
    assert data.subjects[1].entity_type == "Individual"

    assert len(data.transactions) == 1
    tx = data.transactions[0]
    assert tx.amount == "1000.00"
    assert tx.currency == "USD"
    assert tx.originating_account == "Example Origin"
    assert tx.pass_through_accounts == ["123", "456"]
    assert tx.beneficiaries == ["Alice", "Bob"]
    assert tx.uetr == "1234"
    assert tx.notes == "Sample notes"

    # The dataclasses should be JSON serialisable via ``to_dict``.
    json.dumps(data.to_dict())
