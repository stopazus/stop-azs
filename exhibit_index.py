#!/usr/bin/env python3
"""Master Exhibit Index loader and utilities.

This module provides functionality to load, validate, and work with the
Master Exhibit Index (MEI) data structure used to track legal exhibits
in the escrow diversion investigation. The MEI serves as a centralized
registry of all exhibits filed with law enforcement agencies (FBI IC3,
FinCEN, IRS-CI) and provides metadata including:

* Exhibit identifiers (A, B, C, D, E-1, etc.)
* Titles and descriptions
* Filing status
* Bates number ranges
* File names, SHA-256 hashes, and preparation metadata (when applicable)

The module is designed to integrate with existing SAR parser and exhibit
builder tools while maintaining consistency with the repository's minimal
dependency approach.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class Exhibit:
    """Represents a single exhibit in the Master Exhibit Index."""

    exhibit_id: str
    title: str
    status: str
    bates_range: str
    file_name: Optional[str] = None
    sha256_hash: Optional[str] = None
    prepared_by: Optional[str] = None
    prepared_date: Optional[str] = None
    notes: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> Exhibit:
        """Create an Exhibit instance from a dictionary."""
        return cls(
            exhibit_id=data["exhibit_id"],
            title=data["title"],
            status=data["status"],
            bates_range=data["bates_range"],
            file_name=data.get("file_name"),
            sha256_hash=data.get("sha256_hash"),
            prepared_by=data.get("prepared_by"),
            prepared_date=data.get("prepared_date"),
            notes=data.get("notes"),
        )

    def to_dict(self) -> dict:
        """Convert the Exhibit instance to a dictionary."""
        result = {
            "exhibit_id": self.exhibit_id,
            "title": self.title,
            "status": self.status,
            "bates_range": self.bates_range,
        }
        if self.file_name is not None:
            result["file_name"] = self.file_name
        if self.sha256_hash is not None:
            result["sha256_hash"] = self.sha256_hash
        if self.prepared_by is not None:
            result["prepared_by"] = self.prepared_by
        if self.prepared_date is not None:
            result["prepared_date"] = self.prepared_date
        if self.notes is not None:
            result["notes"] = self.notes
        return result


@dataclass
class MasterExhibitIndex:
    """Container for the Master Exhibit Index."""

    exhibits: List[Exhibit]

    @classmethod
    def from_dict(cls, data: dict) -> MasterExhibitIndex:
        """Create a MasterExhibitIndex from a dictionary."""
        exhibits = [Exhibit.from_dict(item) for item in data["Master_Exhibit_Index"]]
        return cls(exhibits=exhibits)

    @classmethod
    def load_from_file(cls, path: Path | str) -> MasterExhibitIndex:
        """Load the Master Exhibit Index from a JSON file."""
        path = Path(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_dict(self) -> dict:
        """Convert the MasterExhibitIndex to a dictionary."""
        return {
            "Master_Exhibit_Index": [exhibit.to_dict() for exhibit in self.exhibits]
        }

    def save_to_file(self, path: Path | str) -> None:
        """Save the Master Exhibit Index to a JSON file."""
        path = Path(path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)
            f.write("\n")

    def get_exhibit_by_id(self, exhibit_id: str) -> Optional[Exhibit]:
        """Retrieve an exhibit by its ID."""
        for exhibit in self.exhibits:
            if exhibit.exhibit_id == exhibit_id:
                return exhibit
        return None

    def get_filed_exhibits(self) -> List[Exhibit]:
        """Get all exhibits with 'Filed' or 'Verified / Filed' status."""
        return [
            exhibit
            for exhibit in self.exhibits
            if "Filed" in exhibit.status
        ]


def load_master_exhibit_index(
    path: Optional[Path | str] = None
) -> MasterExhibitIndex:
    """
    Load the Master Exhibit Index from the default or specified path.

    Args:
        path: Optional path to the master_exhibit_index.json file.
              If not provided, attempts to load from the repository root.

    Returns:
        MasterExhibitIndex instance containing all exhibits.
    """
    if path is None:
        # Try to find the file in the repository root
        repo_root = Path(__file__).resolve().parent
        path = repo_root / "master_exhibit_index.json"
    
    return MasterExhibitIndex.load_from_file(path)


__all__ = [
    "Exhibit",
    "MasterExhibitIndex",
    "load_master_exhibit_index",
]
