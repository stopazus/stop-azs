"""Module entry point for ``python -m sar_parser``."""

from __future__ import annotations

from .cli import main

if __name__ == "__main__":  # pragma: no cover - invoked by interpreter
    raise SystemExit(main())
