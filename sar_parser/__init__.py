"""Public API for the :mod:`sar_parser` package.

This module re-exports the public symbols from sar_parser.validator so users can
import the package surface directly:

    from sar_parser import validate, ValidationError, ValidationResult

It also exposes a best-effort __version__ lookup (falls back to an empty string)
and adds a small convenience alias `validate` -> `validate_string` when that
alias isn't already defined by the validator module.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version as _version
from typing import List

# Best-effort package version lookup (adjust distribution name if needed).
try:
    __version__ = _version("stop-azs")
except PackageNotFoundError:
    __version__ = ""

# Import the validator module and re-export its public API.
from . import validator as _validator  # type: ignore

__all__: List[str] = []

_validator_all = getattr(_validator, "__all__", [])
for _name in _validator_all:
    globals()[_name] = getattr(_validator, _name)
    __all__.append(_name)

# Provide a concise, commonly-used alias for validate_string as `validate`.
if "validate" not in __all__ and "validate_string" in globals():
    validate = globals()["validate_string"]  # type: ignore[name-defined]
    __all__.append("validate")

# Ensure __all__ is stable and unique.
__all__ = list(dict.fromkeys(__all__))
