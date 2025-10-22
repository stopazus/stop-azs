"""Utility to find and optionally remove duplicate files and duplicate lines within files.

This script recursively searches a directory tree and identifies duplicate files based on
size and SHA-256 hashes. By default it prints a summary, but it can also remove duplicate
files when the ``--remove-files`` flag is provided. The first encountered copy of a file is
preserved and later duplicates are deleted.

For text files, the script can also rewrite them with duplicate lines removed via the
``--dedupe-lines`` flag. Line deduplication maintains the original order and only keeps the
first instance of each line. Optional normalization controls case sensitivity and white-
space trimming so "duplicate information" can be cleaned even when formatting varies.

Example usage::

    python tools/deduplicate.py --path . --remove-files --dedupe-lines \
        --strip-whitespace --case-insensitive

This will walk the current repository (ignoring the ``.git`` directory), delete duplicate
files, and rewrite text files so each unique line is present at most once.
"""
from __future__ import annotations

import argparse
import hashlib
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

BUFFER_SIZE = 1024 * 1024
IGNORED_DIRECTORIES = {".git", "__pycache__"}
TEXT_FILE_EXTENSIONS = {
    ".txt",
    ".md",
    ".rst",
    ".cfg",
    ".ini",
    ".json",
    ".yaml",
    ".yml",
    ".py",
    ".toml",
}


def hash_file(path: Path) -> str:
    """Return the SHA-256 hash of ``path``."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(BUFFER_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def iter_files(root: Path, *, follow_symlinks: bool) -> Iterable[Path]:
    """Yield files under ``root`` while respecting ``IGNORED_DIRECTORIES``."""
    for dirpath, dirnames, filenames in os.walk(root, followlinks=follow_symlinks):
        dirnames[:] = [
            name for name in dirnames if name not in IGNORED_DIRECTORIES
        ]
        for filename in filenames:
            yield Path(dirpath, filename)


def group_duplicates(paths: Iterable[Path]) -> Dict[Tuple[int, str], List[Path]]:
    """Group files by size and hash, returning only sets with duplicates."""
    grouped: Dict[Tuple[int, str], List[Path]] = defaultdict(list)
    for path in paths:
        try:
            size = path.stat().st_size
        except OSError:
            continue
        try:
            digest = hash_file(path)
        except OSError:
            continue
        grouped[(size, digest)].append(path)
    return {key: value for key, value in grouped.items() if len(value) > 1}


def dedupe_lines(path: Path, *, strip_whitespace: bool, case_insensitive: bool, dry_run: bool) -> bool:
    """Remove duplicate lines from ``path``.

    Returns ``True`` when the file was modified.
    """
    try:
        original_text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return False

    seen = set()
    result_lines: List[str] = []
    changed = False

    for line in original_text.splitlines(keepends=True):
        key = line
        if strip_whitespace:
            key = key.strip()
        if case_insensitive:
            key = key.lower()
        if key not in seen:
            seen.add(key)
            result_lines.append(line)
        else:
            changed = True

    if not changed:
        return False

    if dry_run:
        return True

    path.write_text("".join(result_lines), encoding="utf-8")
    return True


def remove_duplicate_files(
    duplicates: Dict[Tuple[int, str], Sequence[Path]], *, dry_run: bool
) -> List[Path]:
    """Remove duplicate files, preserving the first occurrence of each group."""
    removed: List[Path] = []
    for paths in duplicates.values():
        original = min(paths, key=lambda item: (len(item.parts), str(item)))
        for path in paths:
            if path == original:
                continue
            removed.append(path)
            if dry_run:
                continue
            try:
                path.unlink()
            except OSError:
                # Continue attempting to clean other files even if we fail here.
                pass
    return removed


def deduplicate(
    root: Path,
    *,
    dry_run: bool,
    follow_symlinks: bool,
    remove_files: bool,
    dedupe_lines_flag: bool,
    strip_whitespace: bool,
    case_insensitive: bool,
) -> None:
    """Coordinate deduplication work based on CLI options."""
    print(f"Scanning {root.resolve()}")
    all_files = list(iter_files(root, follow_symlinks=follow_symlinks))

    duplicates = group_duplicates(all_files)
    if duplicates:
        print(f"Found {sum(len(paths) for paths in duplicates.values()) - len(duplicates)} duplicate file(s).")
        if remove_files:
            removed = remove_duplicate_files(duplicates, dry_run=dry_run)
            if removed:
                action = "Would remove" if dry_run else "Removed"
                for path in removed:
                    print(f"{action}: {path}")
    else:
        print("No duplicate files found.")

    if dedupe_lines_flag:
        text_files = [
            path
            for path in all_files
            if path.suffix.lower() in TEXT_FILE_EXTENSIONS
        ]
        for path in text_files:
            modified = dedupe_lines(
                path,
                strip_whitespace=strip_whitespace,
                case_insensitive=case_insensitive,
                dry_run=dry_run,
            )
            if modified:
                action = "Would rewrite" if dry_run else "Rewrote"
                print(f"{action} with unique lines: {path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find and remove duplicate content.")
    parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="Directory to scan for duplicates (defaults to current working directory).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without making any changes.",
    )
    parser.add_argument(
        "--follow-symlinks",
        action="store_true",
        help="Follow symbolic links while scanning for files.",
    )
    parser.add_argument(
        "--remove-files",
        action="store_true",
        help="Delete duplicate files, preserving the earliest discovered copy.",
    )
    parser.add_argument(
        "--dedupe-lines",
        action="store_true",
        help="Rewrite known text file types with duplicate lines removed.",
    )
    parser.add_argument(
        "--strip-whitespace",
        action="store_true",
        help="Normalize lines by stripping whitespace before deduplicating.",
    )
    parser.add_argument(
        "--case-insensitive",
        action="store_true",
        help="Treat lines that differ only by case as duplicates during line deduplication.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    deduplicate(
        args.path,
        dry_run=args.dry_run,
        follow_symlinks=args.follow_symlinks,
        remove_files=args.remove_files,
        dedupe_lines_flag=args.dedupe_lines,
        strip_whitespace=args.strip_whitespace,
        case_insensitive=args.case_insensitive,
    )


if __name__ == "__main__":
    main()
