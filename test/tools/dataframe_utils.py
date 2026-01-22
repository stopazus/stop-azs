import unittest

import pandas as pd

from tools.dataframe_utils import (
    PRIMARY_SOURCES_COLUMN,
    normalize_primary_sources_column,
)


class NormalizePrimarySourcesColumnTests(unittest.TestCase):
    def test_normalizes_list_cells(self) -> None:
        df = pd.DataFrame(
            {
                PRIMARY_SOURCES_COLUMN: [
                    ["A123", None, "B456", pd.NA],
                    "Already string",
                ]
            }
        )

        result = normalize_primary_sources_column(df)

        self.assertEqual(result.iloc[0], "A123, B456")
        self.assertEqual(result.iloc[1], "Already string")

    def test_respects_custom_column_name(self) -> None:
        df = pd.DataFrame({"Sources": [["Doc1", "Doc2"]]})

        result = normalize_primary_sources_column(df, column="Sources")

        self.assertEqual(result.iloc[0], "Doc1, Doc2")

    def test_raises_when_column_missing(self) -> None:
        df = pd.DataFrame({"Other": ["value"]})

        with self.assertRaises(KeyError):
            normalize_primary_sources_column(df)


if __name__ == "__main__":
    unittest.main()
