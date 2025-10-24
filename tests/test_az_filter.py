import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from stop_azs import find_duplicate_zones, remove_duplicate_zones, summarize_zones


def test_remove_duplicate_zones_preserves_order():
    zones = ["us-east-1a", "us-east-1a", "us-east-1b", "US-EAST-1B", "us-east-1c"]
    assert remove_duplicate_zones(zones) == ["us-east-1a", "us-east-1b", "us-east-1c"]


def test_find_duplicate_zones_case_insensitive():
    zones = ["ZoneA", "zonea", "zoneB", "ZONEb", "zoneC"]
    assert find_duplicate_zones(zones) == ["ZoneA", "zoneB"]


def test_summarize_zones_counts_duplicates():
    zones = ["a", "b", "a", "c", "B"]
    summary = summarize_zones(zones)
    assert summary.total == 5
    assert summary.unique == 3
    assert summary.duplicates == 2
    assert summary.duplicate_zones == ["a", "b"]
    serialized = json.dumps(summary.to_dict())
    assert "duplicate_zones" in serialized


@pytest.mark.parametrize(
    "file_contents,expected",
    [
        ("a\na\nb\n", "a\nb\n"),
        ("us-east-1a\nUS-EAST-1A\n", "us-east-1a\n"),
    ],
)
def test_cli_removes_duplicates(tmp_path: Path, file_contents: str, expected: str):
    from stop_azs.__main__ import main

    file_path = tmp_path / "zones.txt"
    file_path.write_text(file_contents)

    class Capture(list):
        def write(self, data: str) -> None:
            self.append(data)

    capture = Capture()

    # Monkeypatch sys.stdout to capture output.
    import sys

    original_stdout = sys.stdout
    sys.stdout = capture
    try:
        main([str(file_path)])
    finally:
        sys.stdout = original_stdout

    assert "".join(capture) == expected
