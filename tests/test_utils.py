import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sar_parser.utils import load_identifier, pop_any


def test_pop_any_preserves_falsy_values() -> None:
    payload = {"id": 0, "alt": "value"}

    assert pop_any(payload, ["id", "alt"], default="fallback") == 0
    assert "id" not in payload


def test_pop_any_defaults_only_on_none() -> None:
    payload = {"id": None, "alt": "value"}

    assert pop_any(payload, ["id", "alt"], default="fallback") == "fallback"
    assert "id" not in payload


def test_load_identifier_delegates_to_pop_any() -> None:
    payload = {"legacy_id": "", "id": "abc"}

    assert load_identifier(payload, ["legacy_id", "id"], default="fallback") == ""
    assert "legacy_id" not in payload
