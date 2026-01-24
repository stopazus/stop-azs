from pathlib import Path

from sar_parser import parse_sar_file, parse_sar_string


def test_parses_valid_string(valid_sar_xml: str) -> None:
    root = parse_sar_string(valid_sar_xml)
    assert root.tag == "SAR"


def test_parses_valid_file(tmp_path: Path, valid_sar_xml: str) -> None:
    file_path = tmp_path / "sar.xml"
    file_path.write_text(valid_sar_xml, encoding="utf-8")
    root = parse_sar_file(file_path)
    assert root.tag == "SAR"
