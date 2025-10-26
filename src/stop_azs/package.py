"""Helpers for constructing submission packages for regulatory agencies."""

from __future__ import annotations

import os
import re
from pathlib import Path, PureWindowsPath
from typing import Iterable, Mapping, MutableMapping

from .agency import AgencyContact

INVALID_SEGMENTS = {"..", "."}


def _sanitize_segment(segment: str) -> str:
    """Return a safe path segment.

    Leading/trailing whitespace is trimmed and Windows-reserved characters are
    replaced with underscores. Empty segments are ignored.
    """

    cleaned = segment.strip().replace("\\", "")
    if not cleaned:
        return ""
    translation_table = str.maketrans({
        "<": "_",
        ">": "_",
        ":": "-",
        "\"": "'",
        "/": "-",
        "|": "-",
        "?": "_",
        "*": "_",
    })
    normalized = cleaned.translate(translation_table)
    return normalized.strip()


_WINDOWS_DRIVE_PATTERN = re.compile(r"^[a-zA-Z]:")


def _normalize_posix_path(raw_path: str, base: Path) -> Path:
    posix_path = Path(raw_path)
    segments: list[str] = []

    for segment in posix_path.parts:
        if segment in {posix_path.anchor, ""}:
            continue
        if segment in INVALID_SEGMENTS or segment.strip() in INVALID_SEGMENTS:
            raise ValueError("Path segment contains traversal components")
        sanitized = _sanitize_segment(segment)
        if sanitized:
            segments.append(sanitized)

    if not segments and not posix_path.anchor:
        raise ValueError("Path does not contain any valid segments")

    if posix_path.is_absolute():
        root = Path(posix_path.anchor or "/")
        return root.joinpath(*segments)

    if not segments:
        raise ValueError("Path does not contain any valid segments")

    return base.joinpath(*segments)


def normalize_submission_path(path: str | Path, base_dir: str | Path | None = None) -> Path:
    """Normalize a Windows-style path for use on the current platform.

    Parameters
    ----------
    path:
        The raw path as provided by the caller. Windows drive letters are
        ignored and backslashes are treated as separators.
    base_dir:
        Optional base directory to use as the root of the normalized path.

    Returns
    -------
    pathlib.Path
        The normalized path rooted at ``base_dir`` (defaults to the current
        working directory).

    Raises
    ------
    ValueError
        If the path contains traversal segments (``..``) or resolves to an
        empty sequence of components.
    """

    base = Path(base_dir) if base_dir is not None else Path.cwd()
    raw_path = os.fspath(path)

    windows_like = "\\" in raw_path or _WINDOWS_DRIVE_PATTERN.match(raw_path) is not None
    if not windows_like:
        return _normalize_posix_path(raw_path, base)

    windows_path = PureWindowsPath(raw_path)
    parts: list[str] = []

    for segment in windows_path.parts:
        if segment.endswith(":") and len(segment) == 2:
            # Drive letter, skip.
            continue
        if segment in ("/", "\\"):
            continue
        if segment in INVALID_SEGMENTS or segment.strip() in INVALID_SEGMENTS:
            raise ValueError("Path segment contains traversal components")
        sanitized = _sanitize_segment(segment)
        if sanitized:
            parts.append(sanitized)

    if not parts:
        raise ValueError("Path does not contain any valid segments")

    return base.joinpath(*parts)


DEFAULT_AGENCIES: tuple[AgencyContact, ...] = (
    AgencyContact(
        agency="FBI – Internet Crime Complaint Center (IC3)",
        program="Recovery Asset Team (RAT)",
        director="Unit Chief, Recovery Asset Team",
        reference="IC3 Submission ID: 7065f60922b948a59af3a8654edb16dd",
    ),
    AgencyContact(
        agency="FinCEN – BSA E‑Filing",
        program="Suspicious Activity Report (SAR)",
        director="BSA E-Filing Program Director",
    ),
    AgencyContact(
        agency="IRS – Criminal Investigation (IRS‑CI)",
        program="Fraud / Money Laundering Referral",
        director="Chief, IRS Criminal Investigation",
    ),
)


def _write_summary(
    case_dir: Path,
    case_id: str,
    metadata: Mapping[str, str],
    agencies: Iterable[AgencyContact],
) -> None:
    summary_lines = [
        f"# Case Summary: {case_id}",
        "",
        "This package contains submission-ready material for the agencies listed below.",
        "",
    ]

    if metadata:
        summary_lines.append("## Metadata")
        for key, value in metadata.items():
            summary_lines.append(f"- **{key}:** {value}")
        summary_lines.append("")

    summary_lines.append("## Included Agencies")
    summary_lines.append("")
    for agency in agencies:
        details = f"- {agency.agency} — {agency.program}"
        extras: list[str] = [f"Base Code: {agency.base_code()}"]
        if agency.director:
            extras.insert(0, f"Director: {agency.director}")
        summary_lines.append(f"{details} ({'; '.join(extras)})")
    summary_lines.append("")

    case_dir.mkdir(parents=True, exist_ok=True)
    (case_dir / "SUMMARY.md").write_text("\n".join(summary_lines), encoding="utf-8")


def _write_agency_packet(agency_dir: Path, agency: AgencyContact, metadata: Mapping[str, str]) -> None:
    agency_dir.mkdir(parents=True, exist_ok=True)
    lines = [f"# {agency.agency}", "", agency.formatted_block(), ""]
    if metadata:
        lines.append("## Case Metadata")
        for key, value in metadata.items():
            lines.append(f"- **{key}:** {value}")
        lines.append("")
    lines.append("## Next Steps")
    lines.append(
        "Provide supporting documents, timelines, and communications relevant to this agency's remit."
    )
    (agency_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def create_submission_package(
    base_path: str | Path,
    case_id: str,
    agencies: Iterable[AgencyContact] | None = None,
    metadata: Mapping[str, str] | None = None,
) -> Path:
    """Create a structured submission package for the given case.

    Parameters
    ----------
    base_path:
        Root directory where the package will be created.
    case_id:
        Identifier for the case. Used as a directory name beneath ``base_path``.
    agencies:
        Iterable of :class:`AgencyContact` instances. Defaults to
        :data:`DEFAULT_AGENCIES`.
    metadata:
        Additional key/value metadata to embed in generated documents.

    Returns
    -------
    pathlib.Path
        The path to the root of the created package.
    """

    if not case_id or case_id.strip() == "":
        raise ValueError("case_id must be a non-empty string")

    normalized_root = normalize_submission_path(base_path)
    case_dir = normalized_root / case_id.strip()

    metadata_map: Mapping[str, str]
    if metadata is None:
        metadata_map = {}
    elif isinstance(metadata, MutableMapping):
        metadata_map = metadata
    else:
        metadata_map = dict(metadata)

    agency_list = tuple(agencies or DEFAULT_AGENCIES)

    _write_summary(case_dir, case_id.strip(), metadata_map, agency_list)

    for agency in agency_list:
        agency_dir = case_dir / agency.slug()
        _write_agency_packet(agency_dir, agency, metadata_map)

    return case_dir
