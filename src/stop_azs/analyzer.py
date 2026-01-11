"""Helpers for analyzing Stop-AZS payloads."""

from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any


DEFAULT_IDENTIFIER = "unknown"


def pop_any(mapping: MutableMapping[str, Any], *keys: str, default: Any = None) -> Any:
    """Pop the first matching key from a mapping."""

    for key in keys:
        if key in mapping:
            value = mapping.pop(key)
            if value is None:
                return default
            return value
    return default


def load_identifier(payload: MutableMapping[str, Any]) -> Any:
    """Return the identifier for a payload, substituting a default when missing."""

    return pop_any(payload, "identifier", "id", "number", default=DEFAULT_IDENTIFIER)
