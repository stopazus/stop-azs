"""Helpers for building evidentiary bundles for SAR submissions.

The tooling in this module packages a Suspicious Activity Report together
with its supporting artefacts (exhibits, signature, and metadata) into a
single ZIP archive that can be delivered to counterparties or regulators.

The primary helper mirrors the pseudo-code the user supplied during review
but tightens up type handling, ensures deterministic manifests, and always
returns :class:`pathlib.Path` objects for downstream callers.
"""

from __future__ import annotations

import getpass
import json
import platform
import zipfile
from datetime import datetime, timezone
from os import PathLike
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

__all__ = ["create_evidentiary_bundle"]


def _normalise_path(candidate: PathLike[str] | str) -> Path:
    """Return ``candidate`` as an expanded :class:`Path` instance."""

    return Path(candidate).expanduser()


def _gather_exhibits(exhibits_dir: Path) -> List[Path]:
    """Return the list of exhibit files (A–F) inside ``exhibits_dir``."""

    pattern = "Exhibit_[A-F]*"
    exhibits = sorted(exhibits_dir.glob(pattern))
    return [exhibit for exhibit in exhibits if exhibit.is_file()]


def _default_bundle_name(report_path: Path) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    name = f"Exhibit_A-F_Bundle_{timestamp}.zip"
    return report_path.parent / name


def _manifest_payload(
    *,
    exhibits: Sequence[Path],
    report_path: Path,
    supporting_files: Sequence[Path],
    signature_path: Optional[Path],
    meta_path: Optional[Path],
) -> str:
    data = {
        "bundle_generated_utc": datetime.now(timezone.utc).isoformat(),
        "bundle_creator": getpass.getuser(),
        "hostname": platform.node(),
        "exhibits_included": [path.name for path in exhibits],
        "report_file": report_path.name,
        "signature_file": signature_path.name if signature_path else None,
        "meta_file": meta_path.name if meta_path else None,
        "supporting_files": [path.name for path in supporting_files],
    }
    return json.dumps(data, indent=2, sort_keys=True)


def _iter_supporting_paths(report_path: Path) -> Iterable[Path]:
    suffixes = ("", ".sig", ".asc", ".meta")
    for suffix in suffixes:
        if suffix:
            candidate = report_path.with_suffix(report_path.suffix + suffix)
        else:
            candidate = report_path
        if candidate.exists():
            yield candidate


def create_evidentiary_bundle(
    report_path: Path | str,
    exhibits_dir: Path | str,
    bundle_out: Path | str | None = None,
) -> Path:
    """Create a ZIP bundle containing a SAR report and supporting artefacts.

    Parameters
    ----------
    report_path:
        Path to the SAR JSON/XML document that should be bundled.  If the
        corresponding ``.sig`` or ``.meta`` files exist they will be included
        automatically.
    exhibits_dir:
        Directory containing exhibit files following the ``Exhibit_[A-F]``
        naming convention.
    bundle_out:
        Optional output path for the resulting ZIP file.  When omitted a
        timestamped filename is created next to ``report_path``.
    """

    report_path = _normalise_path(report_path)
    exhibits_dir = _normalise_path(exhibits_dir)

    if not report_path.exists():
        raise FileNotFoundError(f"Report file not found: {report_path}")
    if not report_path.is_file():
        raise ValueError(f"Report path must be a file, got: {report_path}")
    if not exhibits_dir.exists():
        raise FileNotFoundError(f"Exhibits directory not found: {exhibits_dir}")
    if not exhibits_dir.is_dir():
        raise ValueError(f"Exhibits path must be a directory, got: {exhibits_dir}")

    if bundle_out is not None:
        bundle_candidate = _normalise_path(bundle_out)
        if bundle_candidate.exists() and bundle_candidate.is_dir():
            bundle_path = bundle_candidate / _default_bundle_name(report_path).name
        else:
            bundle_path = bundle_candidate
    else:
        bundle_path = _default_bundle_name(report_path)

    bundle_path.parent.mkdir(parents=True, exist_ok=True)

    exhibits = _gather_exhibits(exhibits_dir)
    supporting_files = list(_iter_supporting_paths(report_path))

    if not supporting_files:
        raise FileNotFoundError(f"No supporting files found for report: {report_path}")

    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for exhibit in exhibits:
            archive.write(exhibit, exhibit.name)
        for supporting in supporting_files:
            archive.write(supporting, supporting.name)

        signature_candidates = (
            report_path.with_suffix(report_path.suffix + ".sig"),
            report_path.with_suffix(report_path.suffix + ".asc"),
        )
        signature_path = next((candidate for candidate in signature_candidates if candidate.exists()), None)
        meta_candidate = report_path.with_suffix(report_path.suffix + ".meta")
        meta_path = meta_candidate if meta_candidate.exists() else None
        manifest = _manifest_payload(
            exhibits=exhibits,
            report_path=report_path,
            supporting_files=supporting_files,
            signature_path=signature_path,
            meta_path=meta_path,
        )
        archive.writestr("Manifest.json", manifest)

    return bundle_path
