from __future__ import annotations

import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path
from typing import Iterable

DEFAULT_MANIFEST = Path("evidence") / "manifest.json"
DEFAULT_HASHED_DIR = Path("evidence") / "hashed"


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Hash evidence files and maintain a manifest. Use --strict to "
            "re-verify existing entries before proceeding."
        )
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Path to the manifest JSON file (default: evidence/manifest.json)",
    )
    parser.add_argument(
        "--hashed-dir",
        type=Path,
        default=DEFAULT_HASHED_DIR,
        help="Directory containing hashed evidence files (default: evidence/hashed)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Re-verify all manifest entries against the hashed evidence directory "
            "before performing additional work. Any mismatch triggers a non-zero exit."
        ),
    )
    parser.add_argument(
        "--fail-on-inconsistency",
        action="store_true",
        help=(
            "Exit with a non-zero status when the manifest does not match the hashed "
            "evidence files."
        ),
    )
    return parser.parse_args(argv)


def _load_manifest(manifest_path: Path) -> list[dict]:
    if not manifest_path.exists():
        return []

    with manifest_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if isinstance(data, list):
        return data

    if isinstance(data, dict) and isinstance(data.get("files"), list):
        return data["files"]

    raise ValueError(
        "Manifest must be a list of entries or a dictionary containing a 'files' list."
    )


def _hash_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _entry_path(entry: dict) -> Path:
    for key in ("hashed_path", "path", "file", "filename"):
        if key in entry and entry[key]:
            return Path(entry[key])
    raise KeyError("Manifest entry is missing a path identifier (hashed_path/path/file).")


def _entry_hash(entry: dict) -> str:
    for key in ("sha256", "hash", "digest"):
        if key in entry and entry[key]:
            return str(entry[key])
    raise KeyError("Manifest entry is missing a recorded hash (sha256/hash/digest).")


def _verify_entries(entries: list[dict], hashed_dir: Path) -> list[str]:
    discrepancies: list[str] = []

    if not hashed_dir.exists():
        return [f"Hashed directory '{hashed_dir}' does not exist."]

    for entry in entries:
        try:
            relative_path = _entry_path(entry)
            expected_hash = _entry_hash(entry)
        except KeyError as exc:
            discrepancies.append(str(exc))
            continue

        file_path = hashed_dir / relative_path
        if not file_path.exists():
            discrepancies.append(f"Missing hashed file: {file_path}")
            continue

        actual_hash = _hash_file(file_path)
        if actual_hash != expected_hash:
            discrepancies.append(
                f"Hash mismatch for {file_path}: expected {expected_hash}, found {actual_hash}"
            )

    return discrepancies


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(argv)

    entries = _load_manifest(args.manifest)

    should_verify = args.strict or args.fail_on_inconsistency
    exit_on_mismatch = args.strict or args.fail_on_inconsistency

    if should_verify:
        discrepancies = _verify_entries(entries, args.hashed_dir)
        if discrepancies:
            for message in discrepancies:
                print(message, file=sys.stderr)
            if exit_on_mismatch:
                return 1

    # Placeholder for additional logic (e.g., hashing new files) can be added here.
    return 0


if __name__ == "__main__":
    sys.exit(main())
