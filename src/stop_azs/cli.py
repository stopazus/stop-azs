"""Command line interface for the stop-azs analyzer."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .analyzer import load_transactions, total_amount


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze transaction data for anomalies.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze transactions from CSV, JSON, or NDJSON input.",
        description=(
            "Load transactions from a CSV, JSON, or newline-delimited JSON (NDJSON) file "
            "and compute simple aggregates."
        ),
    )
    analyze_parser.add_argument(
        "path",
        type=Path,
        help="Path to the CSV, JSON, or NDJSON file containing transactions.",
    )
    analyze_parser.add_argument(
        "--amount-field",
        default="amount",
        help="Name of the transaction field that holds numeric amounts (default: amount).",
    )

    return parser


def _run_analyze(path: Path, amount_field: str) -> str:
    transactions = load_transactions(path)
    if not transactions:
        return "No transactions found."

    total = total_amount(transactions, amount_field)
    count = len(transactions)
    return (
        f"Processed {count} transactions from {path} with total {amount_field}: {total:.2f}"
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "analyze":
        message = _run_analyze(args.path, args.amount_field)
        print(message)
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
