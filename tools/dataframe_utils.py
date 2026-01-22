"""Helpers for normalizing pandas DataFrame columns used in analysis."""

from __future__ import annotations

import pandas as pd


PRIMARY_SOURCES_COLUMN = "Primary Sources (Bates / Sunbiz / Dockets)"


def normalize_primary_sources_column(
    df: pd.DataFrame,
    column: str = PRIMARY_SOURCES_COLUMN,
) -> pd.Series:
    """Normalize the primary sources column into a comma-delimited string.

    The primary sources column may contain list-valued cells with None/NaN
    entries. This helper coerces list entries into a comma-separated string
    while preserving non-list values.
    """

    if column not in df.columns:
        raise KeyError(f"Missing expected column: {column}")

    def _normalize_cell(value: object) -> object:
        if isinstance(value, list):
            return ", ".join(str(item) for item in value if pd.notna(item))
        return value

    df[column] = df[column].map(_normalize_cell)
    return df[column]
