"""Command line helpers for the :mod:`stop_azs` package."""

from __future__ import annotations

import argparse
import json
from decimal import Decimal
from typing import Sequence

from .analyzer import TransactionAnalyzer, iter_flag_summary, load_transactions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Screen escrow transactions for simple risk indicators")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze a CSV or JSON file of transactions")
    analyze_parser.add_argument("path", help="Path to the transaction file")
    analyze_parser.add_argument(
        "--large-amount-threshold",
        type=Decimal,
        default=Decimal("50000"),
        help="Flag transactions equal to or above this amount",
    )
    analyze_parser.add_argument(
        "--repeat-invoice-threshold",
        type=int,
        default=2,
        help="Flag invoice numbers used by more than this number of unique senders",
    )
    analyze_parser.add_argument(
        "--domestic-country",
        help="ISO country code that should be considered domestic",
    )
    analyze_parser.add_argument(
        "--high-risk-country",
        action="append",
        default=[],
        help="ISO country code to include in the high-risk list (can be provided multiple times)",
    )
    analyze_parser.add_argument(
        "--output",
        choices={"table", "json"},
        default="table",
        help="Output format",
    )
    return parser


def _print_table(results) -> None:
    for tx, flags in results:
        if not flags:
            continue
        print(f"Reference: {tx.reference}  Amount: {tx.amount} {tx.currency}  Receiver: {tx.receiver}")
        for flag in flags:
            detail_parts = ", ".join(f"{key}={value}" for key, value in sorted(flag.details.items()))
            detail_text = f" ({detail_parts})" if detail_parts else ""
            print(f"  - [{flag.code}] {flag.message}{detail_text}")
        print()

    totals = list(iter_flag_summary(results))
    if totals:
        print("Summary of flags:")
        for code, count in totals:
            print(f"  {code}: {count}")


def _print_json(results) -> None:
    payload = []
    for tx, flags in results:
        payload.append(
            {
                "transaction": tx.to_dict(),
                "flags": [
                    {"code": flag.code, "message": flag.message, "details": flag.details}
                    for flag in flags
                ],
            }
        )
    print(json.dumps(payload, indent=2))


def handle_analyze(args: argparse.Namespace) -> int:
    analyzer = TransactionAnalyzer(
        large_amount_threshold=args.large_amount_threshold,
        repeat_invoice_threshold=args.repeat_invoice_threshold,
        domestic_country=args.domestic_country,
        high_risk_countries=args.high_risk_country,
    )
    transactions = load_transactions(args.path)
    results = analyzer.analyze(transactions)
    if args.output == "json":
        _print_json(results)
    else:
        _print_table(results)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "analyze":
        return handle_analyze(args)
    parser.error("Unknown command")
    return 1


if __name__ == "__main__":  # pragma: no cover - convenience for manual execution
    raise SystemExit(main())
