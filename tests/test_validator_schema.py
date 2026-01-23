import pytest

from sar_parser import validate_sar_xml


def test_schema_validation_round_trip(valid_sar_xml: str) -> None:
    pytest.importorskip("xmlschema")
    result = validate_sar_xml(valid_sar_xml.encode("utf-8"))
    assert isinstance(result, dict)
