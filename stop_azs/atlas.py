"""Helpers for downloading and processing the MITRE ATLAS matrix."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any
import importlib.util
import re
import urllib.request

from urllib.error import HTTPError, URLError


_MISSING_PYYAML_MESSAGE = (
    "PyYAML is required to use stop_azs.atlas. "
    "Install the dependencies with `pip install -r requirements.txt`."
)

if importlib.util.find_spec("yaml") is None:  # pragma: no cover - exercised via tests
    raise ModuleNotFoundError(_MISSING_PYYAML_MESSAGE)

import yaml

DEFAULT_ATLAS_DATA_URL = (
    "https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/ATLAS.yaml"
)


_DEFAULT_HTTP_HEADERS = {
    # Mimic pip's user agent style so mirrors like OneDrive serve the raw file
    # instead of an HTML landing page.
    "User-agent": "pip/25.2 stop-azs atlas client",
    "Accept": "application/yaml, text/yaml, text/plain, */*;q=0.1",
}


class AtlasDataError(RuntimeError):
    """Raised when ATLAS data cannot be parsed."""


@dataclass(frozen=True)
class Technique:
    """Representation of an ATLAS technique or subtechnique."""

    id: str
    name: str
    description: str | None
    tactic_ids: tuple[str, ...]
    is_subtechnique: bool
    parent_id: str | None = None
    parent_name: str | None = None

    def display_name(self) -> str:
        """Return a friendly name that includes the parent for subtechniques."""

        if self.is_subtechnique and self.parent_name:
            return f"{self.parent_name}: {self.name}"
        return self.name


_URL_RE = re.compile(r"^https?://", re.IGNORECASE)


def load_atlas_data(source: str | Path | IO[str] | IO[bytes] | None = None) -> Mapping[str, Any]:
    """Load ATLAS data from a URL, path, or open file object."""

    if source is None:
        source = DEFAULT_ATLAS_DATA_URL

    if hasattr(source, "read"):
        text = _read_from_file_object(source)  # type: ignore[arg-type]
    else:
        path = Path(str(source))
        if _URL_RE.match(str(source)):
            text = _read_from_url(str(source))
        elif path.exists():
            text = path.read_text(encoding="utf-8")
        else:
            raise AtlasDataError(f"Could not load ATLAS data from {source!r}")

    data = yaml.safe_load(text)
    if not isinstance(data, Mapping):
        raise AtlasDataError("ATLAS data must decode to a mapping")
    return data


def check_atlas_connection(
    url: str = DEFAULT_ATLAS_DATA_URL, *, timeout: float = 10.0
) -> bool:
    """Verify that the ATLAS dataset can be reached over HTTP."""

    try:
        _probe_url(url, timeout=timeout, method="HEAD")
    except AtlasDataError:
        raise
    except HTTPError as exc:
        if exc.code == 405:
            _probe_url(
                url,
                timeout=timeout,
                method="GET",
                headers={"Range": "bytes=0-0"},
            )
            return True
        raise AtlasDataError(
            f"ATLAS endpoint {url!r} responded with HTTP {exc.code}"
        ) from exc
    except (URLError, OSError) as exc:
        raise AtlasDataError(
            f"Could not reach ATLAS endpoint {url!r}: {exc}"
        ) from exc
    return True


def _probe_url(
    url: str,
    *,
    timeout: float,
    method: str,
    headers: Mapping[str, str] | None = None,
) -> None:
    request_headers = dict(_DEFAULT_HTTP_HEADERS)
    if headers:
        request_headers.update(headers)
    request = urllib.request.Request(
        url,
        method=method,
        headers=request_headers,
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:  # type: ignore[no-untyped-call]
        status = getattr(response, "status", None)
        if status is None:
            try:
                status = response.getcode()
            except AttributeError:
                status = None
        if status is not None and int(status) >= 400:
            raise AtlasDataError(
                f"ATLAS endpoint {url!r} responded with HTTP {status}"
            )


def _read_from_url(url: str) -> str:
    request = urllib.request.Request(url, headers=dict(_DEFAULT_HTTP_HEADERS))
    try:
        with urllib.request.urlopen(request) as response:  # type: ignore[no-untyped-call]
            raw = response.read()
    except OSError as exc:  # pragma: no cover - network errors handled elsewhere
        raise AtlasDataError(f"Could not download ATLAS data: {exc}") from exc
    return raw.decode("utf-8")


def _read_from_file_object(handle: IO[str] | IO[bytes]) -> str:
    contents = handle.read()
    if isinstance(contents, bytes):
        return contents.decode("utf-8")
    return contents


def select_matrix(data: Mapping[str, Any], matrix_id: str = "ATLAS") -> Mapping[str, Any]:
    """Select a matrix from the parsed ATLAS YAML data."""

    matrices = data.get("matrices")
    if not isinstance(matrices, Iterable) or isinstance(matrices, (str, bytes)):
        raise AtlasDataError("ATLAS data does not contain a 'matrices' collection")
    for matrix in matrices:
        if isinstance(matrix, Mapping) and matrix.get("id") == matrix_id:
            return matrix
    raise AtlasDataError(f"Matrix {matrix_id!r} not present in ATLAS data")


def group_techniques_by_tactic(
    matrix: Mapping[str, Any], *, include_subtechniques: bool = True
) -> "OrderedDict[str, list[Technique]]":
    """Group techniques by tactic while preserving order from the source."""

    tactic_lookup: "OrderedDict[str, str]" = OrderedDict()
    raw_tactics = matrix.get("tactics", [])
    if isinstance(raw_tactics, Iterable) and not isinstance(
        raw_tactics, (str, bytes)
    ):
        for tactic in raw_tactics:
            if isinstance(tactic, Mapping):
                tactic_id = tactic.get("id")
                tactic_name = tactic.get("name")
                if isinstance(tactic_id, str) and isinstance(tactic_name, str):
                    tactic_lookup[tactic_id] = tactic_name

    raw_techniques = matrix.get("techniques", [])
    if isinstance(raw_techniques, Iterable) and not isinstance(
        raw_techniques, (str, bytes)
    ):
        techniques = [tech for tech in raw_techniques if isinstance(tech, Mapping)]
    else:
        techniques = []
    technique_lookup: dict[str, Mapping[str, Any]] = {
        str(tech.get("id")): tech for tech in techniques if isinstance(tech.get("id"), str)
    }

    grouped: "OrderedDict[str, list[Technique]]" = OrderedDict(
        (name, []) for name in tactic_lookup.values()
    )

    for tech in techniques:
        tech_id = tech.get("id")
        tech_name = tech.get("name")
        if not isinstance(tech_id, str) or not isinstance(tech_name, str):
            continue

        tactic_ids = _resolve_tactic_ids(tech, technique_lookup)
        if not tactic_ids:
            continue

        is_subtechnique = isinstance(tech.get("subtechnique-of"), str)
        if is_subtechnique and not include_subtechniques:
            continue

        description = tech.get("description") if isinstance(tech.get("description"), str) else None
        parent_id = tech.get("subtechnique-of") if is_subtechnique else None
        parent_name = None
        if is_subtechnique and isinstance(parent_id, str):
            parent = technique_lookup.get(parent_id, {})
            parent_name = parent.get("name") if isinstance(parent.get("name"), str) else None

        technique = Technique(
            id=tech_id,
            name=tech_name,
            description=description,
            tactic_ids=tuple(tactic_ids),
            is_subtechnique=is_subtechnique,
            parent_id=parent_id,
            parent_name=parent_name,
        )

        for tactic_id in tactic_ids:
            tactic_name = tactic_lookup.get(tactic_id)
            if tactic_name is None:
                continue
            grouped.setdefault(tactic_name, []).append(technique)

    return grouped


def _resolve_tactic_ids(
    technique: Mapping[str, Any],
    technique_lookup: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    tactic_ids = technique.get("tactics")
    if isinstance(tactic_ids, Iterable) and not isinstance(tactic_ids, (str, bytes)):
        ids: list[str] = [
            str(tactic_id)
            for tactic_id in tactic_ids
            if isinstance(tactic_id, str)
        ]
        if ids:
            return ids
    parent_id = technique.get("subtechnique-of")
    if isinstance(parent_id, str):
        parent = technique_lookup.get(parent_id)
        if parent:
            return _resolve_tactic_ids(parent, technique_lookup)
    return []


def summarise_matrix(grouped: Mapping[str, Iterable[Technique]]) -> "OrderedDict[str, int]":
    """Return the number of techniques associated with each tactic."""

    summary: "OrderedDict[str, int]" = OrderedDict()
    for tactic_name, techniques in grouped.items():
        summary[str(tactic_name)] = sum(1 for _ in techniques)
    return summary


def _main() -> None:  # pragma: no cover - exercised via CLI invocation
    import argparse
    import sys

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the ATLAS dataset can be reached before downloading",
    )
    parser.add_argument(
        "--source",
        default=DEFAULT_ATLAS_DATA_URL,
        help=(
            "path or URL to the ATLAS dataset (default: official MITRE location)"
        ),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="timeout in seconds for network operations (default: 10)",
    )
    args = parser.parse_args()

    try:
        if args.check:
            check_atlas_connection(args.source, timeout=args.timeout)
            print(
                f"Successfully reached {args.source} with timeout {args.timeout}s"
            )
            return

        data = load_atlas_data(args.source)
        matrix = select_matrix(data)
        grouped = group_techniques_by_tactic(matrix)
        summary = summarise_matrix(grouped)
    except AtlasDataError as exc:  # pragma: no cover - CLI only
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

    for tactic, count in summary.items():
        print(f"{tactic}: {count}")


if __name__ == "__main__":  # pragma: no cover - module CLI entry point
    _main()
