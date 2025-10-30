"""Helpers for validating and summarising casebook bundle archives."""

from __future__ import annotations

import hashlib
import io
import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, Mapping, Optional

__all__ = [
    "BundleMember",
    "ValidationReport",
    "CasebookBundle",
    "parse_sha_manifest",
]

_SHA256_HEX_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def _normalise_manifest_filename(name: str) -> str:
    """Return a normalised filename key used inside manifests.

    The manifest files shipped with the bundles occasionally contain
    redundant leading characters such as ``*`` (used by ``sha256sum`` to
    denote binary files).  Normalising allows the rest of the code to work
    with clean filenames.
    """

    name = name.strip()
    if name.startswith(("*", " ")):
        name = name[1:]
    return name.strip()


def parse_sha_manifest(manifest_text: str) -> Dict[str, str]:
    """Parse a SHA manifest into a mapping.

    The manifest is expected to contain one file per line using a variety of
    formats produced by ``sha256sum`` and related tools.  Supported line
    layouts include the following examples::

        f1b2...  Binder_Metadata.json
        SHA256 (Master_Casebook_Bundle_vNext.pdf) = f1b2...
        README.txt: f1b2...

    Blank lines and comment lines starting with ``#`` are ignored.
    ``ValueError`` is raised if a line cannot be parsed, when the manifest
    does not contain any entries, or when the same filename appears with
    conflicting digests.
    """

    if manifest_text is None:
        raise ValueError("manifest_text must be provided")

    # Strip a UTF-8 byte order mark if present. Some manifest generators emit
    # BOM-prefixed text files which would otherwise make the first digest fail
    # to match the expected pattern.
    manifest_text = manifest_text.lstrip("\ufeff")

    entries: Dict[str, str] = {}

    for index, raw_line in enumerate(manifest_text.splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        digest: Optional[str] = None
        filename: Optional[str] = None
        raw_filename: Optional[str] = None

        # sha256sum format: ``<digest><two spaces><filename>`` optionally
        # prefixed by ``*`` before the filename.
        if len(line) > 64 and _SHA256_HEX_RE.match(line[:64]):
            digest = line[:64].lower()
            raw_filename = raw_line[64:]

        # BSD format: ``SHA256 (<filename>) = <digest>``
        if digest is None:
            match = re.match(
                r"(?i)sha(?:256)?\s*\((.+)\)\s*=\s*([0-9a-fA-F]{64})$",
                line,
            )
            if match:
                raw_filename = match.group(1)
                digest = match.group(2).lower()

        # ``filename: digest``
        if digest is None and ":" in line:
            left, right = line.split(":", 1)
            candidate_digest = right.strip()
            if _SHA256_HEX_RE.match(candidate_digest):
                raw_filename = left
                digest = candidate_digest.lower()

        # ``digest filename`` (single space)
        if digest is None:
            parts = line.split()
            if len(parts) >= 2 and _SHA256_HEX_RE.match(parts[0]):
                digest = parts[0].lower()
                raw_filename = raw_line[len(parts[0]) :]

        if raw_filename is not None:
            filename = _normalise_manifest_filename(raw_filename)

        if not filename or not digest:
            raise ValueError(
                f"Unrecognised manifest line {index}: {raw_line!r}"
            )

        if filename in entries and entries[filename] != digest:
            raise ValueError(
                "Manifest contains duplicate entry for "
                f"{filename!r} with different digests"
            )

        entries[filename] = digest

    if not entries:
        raise ValueError("manifest did not contain any entries")

    return entries


@dataclass(frozen=True)
class BundleMember:
    """Represents a file stored inside the bundle archive."""

    name: str
    size: int
    sha256: str
    data: bytes

    def open(self) -> io.BytesIO:
        """Return the member contents as a file-like object."""

        return io.BytesIO(self.data)


@dataclass(frozen=True)
class ValidationReport:
    """Details discrepancies observed while validating a bundle."""

    missing_from_archive: tuple[str, ...]
    missing_from_manifest: tuple[str, ...]
    mismatched_digests: Mapping[str, tuple[str, str]]

    @property
    def is_valid(self) -> bool:
        """Return ``True`` when no validation issues were discovered."""

        return (
            not self.missing_from_archive
            and not self.missing_from_manifest
            and not self.mismatched_digests
        )


class CasebookBundle:
    """Represents an extracted ``Master_Casebook`` bundle."""

    MANIFEST_FILENAME = "SHA-Manifest.txt"
    METADATA_FILENAME = "Binder_Metadata.json"

    def __init__(self, members: Mapping[str, BundleMember], manifest: Mapping[str, str]):
        self._members = dict(members)
        self._manifest = dict(manifest)
        self._metadata = self._load_metadata()

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    @classmethod
    def load(cls, source: str | Path | bytes | io.BufferedIOBase) -> "CasebookBundle":
        """Load a bundle from *source*.

        ``source`` may be a path-like object, ``bytes`` containing an entire
        archive, or an open binary file object positioned at the start of a
        zip archive.
        """

        if isinstance(source, (str, Path)):
            with zipfile.ZipFile(source) as archive:
                members = cls._read_members(archive)
        else:
            if isinstance(source, bytes):
                file_obj: io.BufferedIOBase = io.BytesIO(source)
            else:
                file_obj = source
            with zipfile.ZipFile(file_obj) as archive:
                members = cls._read_members(archive)

        manifest_member = members.get(cls.MANIFEST_FILENAME)
        if manifest_member is None:
            raise FileNotFoundError(
                f"Bundle missing required {cls.MANIFEST_FILENAME} entry"
            )
        manifest_text = manifest_member.data.decode("utf-8-sig")
        manifest = parse_sha_manifest(manifest_text)
        return cls(members, manifest)

    @staticmethod
    def _read_members(archive: zipfile.ZipFile) -> Dict[str, BundleMember]:
        members: Dict[str, BundleMember] = {}
        for info in archive.infolist():
            if info.is_dir():
                continue
            data = archive.read(info.filename)
            digest = hashlib.sha256(data).hexdigest()
            members[info.filename] = BundleMember(
                name=info.filename,
                size=info.file_size,
                sha256=digest,
                data=data,
            )
        return members

    def _load_metadata(self) -> Mapping[str, object]:
        metadata_member = self._members.get(self.METADATA_FILENAME)
        if not metadata_member:
            return {}
        try:
            return json.loads(metadata_member.data.decode("utf-8-sig"))
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive guard
            raise ValueError("Binder metadata is not valid JSON") from exc

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def manifest(self) -> Mapping[str, str]:
        return self._manifest

    @property
    def metadata(self) -> Mapping[str, object]:
        return self._metadata

    @property
    def members(self) -> Mapping[str, BundleMember]:
        return self._members

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------
    def get_member(self, name: str) -> BundleMember:
        try:
            return self._members[name]
        except KeyError as exc:
            raise KeyError(f"Unknown bundle member: {name}") from exc

    def iter_members(self) -> Iterator[BundleMember]:
        return iter(self._members.values())

    def validate(self) -> ValidationReport:
        manifest_names = set(self._manifest)
        archive_names = set(self._members)

        missing_from_archive = tuple(sorted(manifest_names - archive_names))

        # Exclude the manifest itself from the "missing from manifest" list to
        # avoid reporting it when a manifest omits itself.
        archive_missing_manifest = archive_names - manifest_names
        archive_missing_manifest -= {self.MANIFEST_FILENAME}
        missing_from_manifest = tuple(sorted(archive_missing_manifest))

        mismatched: Dict[str, tuple[str, str]] = {}
        for name in sorted(manifest_names & archive_names):
            expected = self._manifest[name].lower()
            actual = self._members[name].sha256.lower()
            if expected != actual:
                mismatched[name] = (expected, actual)

        return ValidationReport(
            missing_from_archive=missing_from_archive,
            missing_from_manifest=missing_from_manifest,
            mismatched_digests=mismatched,
        )

    def summary(self) -> Mapping[str, object]:
        """Return a dictionary describing bundle contents."""

        return {
            "file_count": len(self._members),
            "manifest_entries": len(self._manifest),
            "metadata": self._metadata,
            "members": [
                {
                    "name": member.name,
                    "size": member.size,
                    "sha256": member.sha256,
                }
                for member in sorted(self._members.values(), key=lambda m: m.name)
            ],
        }

