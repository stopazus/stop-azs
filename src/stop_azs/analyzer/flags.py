"""Definitions for analyzer flag metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass(frozen=True, slots=True)
class SuspicionFlag:
    """Represents a single heuristic that flagged a transaction."""

    code: str
    message: str
    details: Dict[str, object] = field(default_factory=dict)


__all__ = ["SuspicionFlag"]
