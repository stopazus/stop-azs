"""Utilities for loading and analyzing transaction data."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, List, Mapping

Transaction = Mapping[str, object]


def load_transactions(path: Path) -> List[Transaction]:
    """Load transactions from a CSV, JSON, or NDJSON file.

    Parameters
    ----------
    path:
        Path to the input file. The loader detects the format using the
        file extension.

    Returns
    -------
    list of dict
        A list of transaction dictionaries, where the keys correspond to the
        column names (for CSV) or object properties (for JSON/NDJSON).

    Raises
    ------
    ValueError
        If the file extension is not recognised or if the file contents are
        not compatible with the expected structure.
    """

    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return _load_csv(path)
    if suffix == ".json":
        return _load_json(path)
    if suffix in {".ndjson", ".jsonl"}:
        return _load_ndjson(path)

    raise ValueError(f"Unsupported transaction format: {path}")


def _load_csv(path: Path) -> List[Transaction]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader]


def _load_json(path: Path) -> List[Transaction]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)

    if isinstance(data, list):
        return [dict(item) for item in data]

    raise ValueError("JSON transaction files must contain a top-level array.")


def _load_ndjson(path: Path) -> List[Transaction]:
    transactions: List[Transaction] = []

    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError as exc:  # pragma: no cover - guard clause
                raise ValueError(
                    f"Invalid JSON object on line {line_number} of {path}"
                ) from exc
            if not isinstance(record, dict):
                raise ValueError(
                    f"NDJSON line {line_number} in {path} did not contain an object"
                )
            transactions.append(record)

    return transactions


def total_amount(transactions: Iterable[Mapping[str, object]], field: str) -> float:
    """Compute the total numeric amount stored in ``field`` across transactions."""

    total = 0.0
    for tx in transactions:
        value = tx.get(field)
        if value is None:
            continue
        try:
            total += float(value)
        except (TypeError, ValueError) as exc:  # pragma: no cover - defensive
            raise ValueError(
                f"Transaction field '{field}' must be numeric (got {value!r})."
            ) from exc
    return total


__all__ = ["load_transactions", "total_amount"]
