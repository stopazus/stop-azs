import pytest

from sar_parser import SarParseError, parse_sar_string


def test_rejects_non_sar_root() -> None:
    with pytest.raises(SarParseError, match="Root element must be <SAR>"):
        parse_sar_string("<NotSar />")


def test_rejects_malformed_xml() -> None:
    with pytest.raises(SarParseError, match="Malformed XML"):
        parse_sar_string("<SAR>")
