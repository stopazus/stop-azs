import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for path in (ROOT, SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from stop_azs import analyzer


class LoadIdentifierTests(unittest.TestCase):
    def test_numeric_identifier_is_preserved(self) -> None:
        payload = {"id": 0}
        identifier = analyzer.load_identifier(payload)
        self.assertEqual(identifier, 0)

    def test_default_identifier_used_when_missing(self) -> None:
        payload = {}
        identifier = analyzer.load_identifier(payload)
        self.assertEqual(identifier, analyzer.DEFAULT_IDENTIFIER)


if __name__ == "__main__":
    unittest.main()
