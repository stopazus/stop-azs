"""Command line interface for the ``sar_parser`` toolkit."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional, Sequence

from .bundler import create_evidentiary_bundle

__all__ = ["main", "build_parser"]


def _path(value: str) -> Path:
    return Path(value).expanduser()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sar-parser",
        description="Utility commands for packaging and signing Suspicious Activity Reports.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    bundle = sub.add_parser(
        "bundle",
        help="Package exhibits and signed report into court-ready ZIP",
    )
    bundle.add_argument(
        "--report",
        type=_path,
        required=True,
        help="Signed evidentiary JSON/XML report",
    )
    bundle.add_argument(
        "--exhibits",
        type=_path,
        required=True,
        help="Directory containing Exhibit A–F files",
    )
    bundle.add_argument(
        "--out",
        type=_path,
        help="Optional output path for ZIP (file or directory)",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "bundle":
        create_evidentiary_bundle(args.report, args.exhibits, args.out)
        return 0
    parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
