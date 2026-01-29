import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exhibit_index import Exhibit, MasterExhibitIndex, load_master_exhibit_index


class ExhibitTests(unittest.TestCase):
    def test_from_dict_minimal(self) -> None:
        data = {
            "exhibit_id": "A",
            "title": "Test Exhibit",
            "status": "Filed",
            "bates_range": "NST-A-0001 → NST-A-0015",
        }
        exhibit = Exhibit.from_dict(data)
        self.assertEqual(exhibit.exhibit_id, "A")
        self.assertEqual(exhibit.title, "Test Exhibit")
        self.assertEqual(exhibit.status, "Filed")
        self.assertEqual(exhibit.bates_range, "NST-A-0001 → NST-A-0015")
        self.assertIsNone(exhibit.file_name)
        self.assertIsNone(exhibit.sha256_hash)

    def test_from_dict_complete(self) -> None:
        data = {
            "exhibit_id": "E-1",
            "title": "Wire Disbursement",
            "status": "Verified / Filed",
            "bates_range": "NST-E1-0001 → NST-E1-0003",
            "file_name": "Exhibit_E1_Wire.pdf",
            "sha256_hash": "44015903de5e37fd918a474aad22fcce8bcb455c7d2caa7259d792cacf4cdf91",
            "prepared_by": "N & S Holding LLC",
            "prepared_date": "2025-10-20",
            "notes": "Test notes",
        }
        exhibit = Exhibit.from_dict(data)
        self.assertEqual(exhibit.exhibit_id, "E-1")
        self.assertEqual(exhibit.file_name, "Exhibit_E1_Wire.pdf")
        self.assertEqual(
            exhibit.sha256_hash,
            "44015903de5e37fd918a474aad22fcce8bcb455c7d2caa7259d792cacf4cdf91",
        )
        self.assertEqual(exhibit.prepared_by, "N & S Holding LLC")
        self.assertEqual(exhibit.prepared_date, "2025-10-20")
        self.assertEqual(exhibit.notes, "Test notes")

    def test_to_dict_minimal(self) -> None:
        exhibit = Exhibit(
            exhibit_id="A",
            title="Test Exhibit",
            status="Filed",
            bates_range="NST-A-0001 → NST-A-0015",
        )
        result = exhibit.to_dict()
        self.assertEqual(result["exhibit_id"], "A")
        self.assertNotIn("file_name", result)
        self.assertNotIn("sha256_hash", result)

    def test_to_dict_complete(self) -> None:
        exhibit = Exhibit(
            exhibit_id="E-1",
            title="Wire Disbursement",
            status="Verified / Filed",
            bates_range="NST-E1-0001 → NST-E1-0003",
            file_name="test.pdf",
            sha256_hash="abc123",
            prepared_by="Test",
            prepared_date="2025-10-20",
            notes="Test notes",
        )
        result = exhibit.to_dict()
        self.assertEqual(result["file_name"], "test.pdf")
        self.assertEqual(result["sha256_hash"], "abc123")
        self.assertEqual(result["notes"], "Test notes")


class MasterExhibitIndexTests(unittest.TestCase):
    def test_from_dict(self) -> None:
        data = {
            "Master_Exhibit_Index": [
                {
                    "exhibit_id": "A",
                    "title": "Test A",
                    "status": "Filed",
                    "bates_range": "NST-A-0001 → NST-A-0015",
                },
                {
                    "exhibit_id": "B",
                    "title": "Test B",
                    "status": "Filed",
                    "bates_range": "NST-B-0001 → NST-B-0006",
                },
            ]
        }
        index = MasterExhibitIndex.from_dict(data)
        self.assertEqual(len(index.exhibits), 2)
        self.assertEqual(index.exhibits[0].exhibit_id, "A")
        self.assertEqual(index.exhibits[1].exhibit_id, "B")

    def test_get_exhibit_by_id(self) -> None:
        data = {
            "Master_Exhibit_Index": [
                {
                    "exhibit_id": "A",
                    "title": "Test A",
                    "status": "Filed",
                    "bates_range": "NST-A-0001 → NST-A-0015",
                },
                {
                    "exhibit_id": "B",
                    "title": "Test B",
                    "status": "Filed",
                    "bates_range": "NST-B-0001 → NST-B-0006",
                },
            ]
        }
        index = MasterExhibitIndex.from_dict(data)
        
        exhibit_a = index.get_exhibit_by_id("A")
        self.assertIsNotNone(exhibit_a)
        self.assertEqual(exhibit_a.title, "Test A")
        
        exhibit_b = index.get_exhibit_by_id("B")
        self.assertIsNotNone(exhibit_b)
        self.assertEqual(exhibit_b.title, "Test B")
        
        exhibit_missing = index.get_exhibit_by_id("Z")
        self.assertIsNone(exhibit_missing)

    def test_get_filed_exhibits(self) -> None:
        data = {
            "Master_Exhibit_Index": [
                {
                    "exhibit_id": "A",
                    "title": "Test A",
                    "status": "Filed",
                    "bates_range": "NST-A-0001 → NST-A-0015",
                },
                {
                    "exhibit_id": "B",
                    "title": "Test B",
                    "status": "Pending",
                    "bates_range": "NST-B-0001 → NST-B-0006",
                },
                {
                    "exhibit_id": "C",
                    "title": "Test C",
                    "status": "Verified / Filed",
                    "bates_range": "NST-C-0001 → NST-C-0004",
                },
            ]
        }
        index = MasterExhibitIndex.from_dict(data)
        
        filed = index.get_filed_exhibits()
        self.assertEqual(len(filed), 2)
        self.assertIn("A", [e.exhibit_id for e in filed])
        self.assertIn("C", [e.exhibit_id for e in filed])
        self.assertNotIn("B", [e.exhibit_id for e in filed])

    def test_load_from_file(self) -> None:
        # This test loads the actual master_exhibit_index.json file
        mei_path = ROOT / "master_exhibit_index.json"
        if mei_path.exists():
            index = MasterExhibitIndex.load_from_file(mei_path)
            self.assertGreater(len(index.exhibits), 0)
            
            # Verify structure of loaded exhibits
            for exhibit in index.exhibits:
                self.assertIsInstance(exhibit.exhibit_id, str)
                self.assertIsInstance(exhibit.title, str)
                self.assertIsInstance(exhibit.status, str)
                self.assertIsInstance(exhibit.bates_range, str)


if __name__ == "__main__":
    unittest.main()
