"""Helpers for loading transactions from serialized formats."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import List

from .transaction import Transaction


def load_transactions(path: str | Path, *, encoding: str = "utf-8") -> List[Transaction]:
    """Load transactions from a CSV, JSON, or newline-delimited JSON (NDJSON) document."""

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Cannot locate transaction file: {file_path}")

    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        with file_path.open("r", encoding=encoding, newline="") as handle:
            reader = csv.DictReader(handle)
            return [Transaction.from_dict(row) for row in reader]
    if suffix == ".ndjson":
        with file_path.open("r", encoding=encoding) as handle:
            return [
                Transaction.from_dict(json.loads(line))
                for line in handle
                if line.strip()
            ]
    if suffix == ".json":
        with file_path.open("r", encoding=encoding) as handle:
            data = json.load(handle)
        if isinstance(data, dict):
            data = data.get("transactions", [])
        if not isinstance(data, list):
            raise ValueError("JSON transaction payload must be a list")
        return [Transaction.from_dict(item) for item in data]

    raise ValueError("Unsupported file format. Expected CSV, JSON, or NDJSON.")


__all__ = ["load_transactions"]
