import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture()
def valid_sar_xml() -> str:
    return """\
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
