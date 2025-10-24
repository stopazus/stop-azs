"""Command line interface for the stop-azs utilities."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable, List

from .az_filter import find_duplicate_zones, remove_duplicate_zones, summarize_zones


def _read_zones(paths: List[Path]) -> List[str]:
    zones: List[str] = []
    for path in paths:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    zones.append(line)
    return zones


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Find and remove duplicate availability zones from newline delimited files"
        )
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Files containing availability zones (one per line). Reads stdin when omitted.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a JSON summary instead of the unique zone list.",
    )
    parser.add_argument(
        "--duplicates",
        action="store_true",
        help="Only print the duplicates instead of the cleaned list.",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(argv)

    if args.paths:
        zones = _read_zones(args.paths)
    else:
        zones = [line.strip() for line in sys.stdin if line.strip()]

    if args.summary:
        summary = summarize_zones(zones)
        print(json.dumps(summary.to_dict(), indent=2))
    elif args.duplicates:
        for zone in find_duplicate_zones(zones):
            print(zone)
    else:
        for zone in remove_duplicate_zones(zones):
            print(zone)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
