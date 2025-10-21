"""Core utilities for finding and removing duplicate availability zones."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable, List, Sequence


@dataclass(frozen=True)
class ZoneSummary:
    """Summary information about a collection of availability zones."""

    total: int
    unique: int
    duplicates: int
    duplicate_zones: List[str]

    def to_dict(self) -> dict[str, int | List[str]]:
        """Return a JSON-serialisable representation of the summary."""

        return {
            "total": self.total,
            "unique": self.unique,
            "duplicates": self.duplicates,
            "duplicate_zones": list(self.duplicate_zones),
        }


def _normalise(zone: str) -> str:
    """Normalise an availability zone string for comparison."""

    return zone.strip().lower()


def find_duplicate_zones(zones: Sequence[str]) -> List[str]:
    """Return a sorted list of duplicate availability zones.

    Parameters
    ----------
    zones:
        The zones to inspect.

    Returns
    -------
    list[str]
        The zones that appear more than once, case-insensitively. The original
        capitalisation of the first occurrence is preserved.
    """

    seen = {}
    duplicates: set[str] = set()

    for zone in zones:
        key = _normalise(zone)
        if key in seen:
            duplicates.add(seen[key])
        else:
            seen[key] = zone

    return sorted(duplicates, key=_normalise)


def remove_duplicate_zones(zones: Iterable[str]) -> List[str]:
    """Return *zones* with duplicates removed while preserving order."""

    seen = set()
    unique_zones: List[str] = []

    for zone in zones:
        key = _normalise(zone)
        if key not in seen:
            seen.add(key)
            unique_zones.append(zone)

    return unique_zones


def summarize_zones(zones: Sequence[str]) -> ZoneSummary:
    """Return a :class:`ZoneSummary` describing *zones*."""

    total = len(zones)
    unique_zones = remove_duplicate_zones(zones)
    counts = Counter(_normalise(zone) for zone in zones)
    duplicate_zones = sorted(
        (zone for zone, count in counts.items() if count > 1),
    )
    duplicate_display = [
        next(original for original in zones if _normalise(original) == dup)
        for dup in duplicate_zones
    ]

    return ZoneSummary(
        total=total,
        unique=len(unique_zones),
        duplicates=total - len(unique_zones),
        duplicate_zones=duplicate_display,
    )
