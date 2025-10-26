"""Command-line interface for SAR validation."""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from .validation import SarValidator, ValidationIssue


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate FinCEN SAR XML filings and generate a report.",
    )
    parser.add_argument(
        "--validate-dir",
        type=Path,
        required=True,
        help="Directory containing SAR XML filings to validate.",
    )
    parser.add_argument(
        "--export-report",
        type=Path,
        help="Path to export a JSON validation report.",
    )
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    directory: Path = args.validate_dir
    if not directory.exists() or not directory.is_dir():
        parser.error(f"Validation directory '{directory}' does not exist or is not a directory.")

    files = sorted(
        [p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in {".xml", ".sar"}]
    )

    if not files:
        print(f"No SAR XML files were found in {directory}.")
        return 1

    validator = SarValidator()

    results: Dict[Path, List[ValidationIssue]] = {}
    total_errors = 0
    total_warnings = 0

    for file_path in files:
        issues = validator.validate_file(file_path)
        results[file_path] = issues
        total_errors += sum(1 for issue in issues if issue.severity == "error")
        total_warnings += sum(1 for issue in issues if issue.severity == "warning")

    _print_report(results, total_errors, total_warnings)

    if args.export_report:
        _export_report(args.export_report, directory, results, total_errors, total_warnings)

    return 0 if total_errors == 0 else 2


def _print_report(
    results: Dict[Path, List[ValidationIssue]], total_errors: int, total_warnings: int
) -> None:
    print("SAR Validation Report")
    print("=" * 23)
    for path, issues in results.items():
        print(f"\nFile: {path}")
        if not issues:
            print("  No issues found.")
            continue
        for issue in issues:
            detail = f"  - [{issue.severity.upper()}] {issue.message} ({issue.code})"
            if issue.context:
                detail += f" [{issue.context}]"
            print(detail)

    print("\nSummary")
    print("-" * 7)
    print(f"Files scanned : {len(results)}")
    print(f"Errors        : {total_errors}")
    print(f"Warnings      : {total_warnings}")


def _export_report(
    export_path: Path,
    directory: Path,
    results: Dict[Path, List[ValidationIssue]],
    total_errors: int,
    total_warnings: int,
) -> None:
    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "root_directory": str(directory.resolve()),
        "summary": {
            "files_scanned": len(results),
            "errors": total_errors,
            "warnings": total_warnings,
        },
        "files": [
            {
                "path": str(path.resolve()),
                "issues": [issue.to_dict() for issue in issues],
            }
            for path, issues in results.items()
        ],
    }

    export_path.parent.mkdir(parents=True, exist_ok=True)
    export_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Exported JSON report to {export_path}")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
