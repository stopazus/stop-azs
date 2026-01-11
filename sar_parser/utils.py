"""Utility helpers for parsing SAR payloads."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Mapping, MutableMapping


def pop_any(
    data: MutableMapping[str, Any],
    keys: Iterable[str],
    default: Any | None = None,
) -> Any | None:
    """Pop the first matching key from ``data``.

    Defaults are only applied when a matching key exists and its value is ``None``,
    or when none of the keys are present at all. Falsy values (e.g., ``0`` or
    empty strings) are preserved.
    """

    for key in keys:
        if key in data:
            value = data.pop(key)
            if value is None:
                return default
            return value
    return default


def load_identifier(
    data: MutableMapping[str, Any],
    keys: Iterable[str],
    default: Any | None = None,
) -> Any | None:
    """Load an identifier from ``data`` using the first available key."""

    return pop_any(data, keys, default=default)


__all__ = ["load_identifier", "pop_any"]
