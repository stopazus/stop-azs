"""Helper utilities for working with mapping-like payloads."""

from __future__ import annotations

from typing import Iterable, MutableMapping, TypeVar


T = TypeVar("T")


def pop_any(mapping: MutableMapping[str, T], keys: Iterable[str], default: T | None = None) -> T | None:
    """Pop the first matching key from *mapping*.

    The helper looks for the provided *keys* in order and removes the first
    one found from *mapping*, returning the associated value.  When no key is
    present, *default* is returned instead.

    Parameters
    ----------
    mapping:
        The mutable mapping to inspect.
    keys:
        An iterable of keys that will be attempted in order.
    default:
        The value to return when no keys are present.  ``None`` is used when no
        default is supplied.
    """

    for key in keys:
        if key in mapping:
            return mapping.pop(key)
    return default
