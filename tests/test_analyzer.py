import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sar_parser.analyzer import REPEATED_INVOICE, Transaction, analyze_transactions


class AnalyzerTests(unittest.TestCase):
    def test_repeated_invoice_counts_unique_senders(self) -> None:
        transactions = [
            Transaction(sender="Sender A", invoice="INV-100"),
            Transaction(sender="Sender A", invoice="INV-100"),
            Transaction(sender="Sender B", invoice="INV-200"),
            Transaction(sender="Sender C", invoice="INV-200"),
        ]

        flags = analyze_transactions(transactions)

        flagged = [index for index, codes in enumerate(flags) if REPEATED_INVOICE in codes]
        self.assertEqual(flagged, [2, 3])

        expected_flags = {2: {REPEATED_INVOICE}, 3: {REPEATED_INVOICE}}
        for index, expected in expected_flags.items():
            with self.subTest(index=index):
                self.assertEqual(flags[index], expected)


if __name__ == "__main__":
    unittest.main()
