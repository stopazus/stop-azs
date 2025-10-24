"""Utilities for working with Suspicious Activity Report (SAR) documents.

This package currently focuses on tooling that supports packaging and signing
SAR payloads for exchange with counterparties.  The helper functions are
intentionally dependency free so they can run in restricted environments (such
as air-gapped compliance desktops).
"""

from __future__ import annotations

from importlib import import_module
from typing import Any, List, Set

from .bundler import create_evidentiary_bundle

_SIGNING_EXPORTS: Set[str] = {
    "DEFAULT_ALGORITHM",
    "SUPPORTED_ALGORITHMS",
    "Signature",
    "SignatureError",
    "sign_file_with_gpg",
    "sign_payload",
    "verify_signature",
}

__all__ = ["create_evidentiary_bundle", *_SIGNING_EXPORTS]


def __getattr__(name: str) -> Any:
    if name in _SIGNING_EXPORTS:
        module = import_module(".signing", __name__)
        return getattr(module, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__() -> List[str]:  # pragma: no cover - convenience for interactive use
    return sorted(set(globals()) | _SIGNING_EXPORTS)
