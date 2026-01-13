"""Live validation helper utilities.

This module provides a light-weight file monitor that re-runs the SAR
validator whenever the watched document changes on disk.  It avoids any
platform-specific file watching dependencies by relying on portable
``stat`` metadata (modification time and file size).  The monitor can be
used programmatically or via ``python -m sar_parser.live_update`` to
print validation updates in real time.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import argparse
import hashlib
import sys
import time
from typing import Callable, Iterable, Iterator, Optional

from .validator import ValidationResult, validate_string


Signature = str
Validator = Callable[[str], ValidationResult]


@dataclass(slots=True)
class LiveUpdate:
    """Container describing the validation state of a file at a point in time."""

    path: Path
    timestamp: float
    result: ValidationResult

    def iso_timestamp(self) -> str:
        """Return an ISO 8601 representation of :attr:`timestamp`."""

        return datetime.fromtimestamp(self.timestamp).isoformat(timespec="seconds")


class LiveUpdateMonitor:
    """Poll a SAR document on disk and emit validation updates when it changes."""

    def __init__(self, path: "str | Path", *, validator: Validator = validate_string) -> None:
        self.path = Path(path)
        self._validator = validator
        self._last_signature: Optional[Signature] = None

    def poll_once(self) -> Optional[LiveUpdate]:
        """Return a :class:`LiveUpdate` if the file changed since the last call."""

        try:
            text = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            # Reset the cached signature so that a re-created file triggers
            # validation on the next successful poll.
            self._last_signature = None
            return None

        signature: Signature = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if signature == self._last_signature:
            return None

        self._last_signature = signature
        result = self._validator(text)
        return LiveUpdate(path=self.path, timestamp=time.time(), result=result)

    def run(self, interval: float = 1.0) -> Iterator[LiveUpdate]:
        """Yield updates forever, pausing ``interval`` seconds between polls."""

        if interval <= 0:
            raise ValueError("interval must be positive")

        while True:
            update = self.poll_once()
            if update is not None:
                yield update
            time.sleep(interval)


def _format_result(result: ValidationResult) -> str:
    if result.is_valid:
        return "Validation passed – no errors detected."

    lines = ["Validation failed – detected errors:"]
    for error in result.errors:
        location = f" ({error.location})" if error.location else ""
        lines.append(f"  - {error.message}{location}")
    return "\n".join(lines)


def _cli(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Live SAR XML validator")
    parser.add_argument("path", help="Path to the SAR XML file to monitor")
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Polling interval in seconds (default: 1.0)",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    monitor = LiveUpdateMonitor(args.path)
    print(
        f"Watching {monitor.path} – polling every {args.interval:.2f}s. Press Ctrl+C to stop.",
        flush=True,
    )

    try:
        for update in monitor.run(interval=args.interval):
            print(f"[{update.iso_timestamp()}] {_format_result(update.result)}", flush=True)
    except KeyboardInterrupt:  # pragma: no cover - interactive path
        print("\nStopped monitoring.")
        return 0

    return 0


def main() -> None:  # pragma: no cover - thin CLI wrapper
    sys.exit(_cli())


__all__ = ["LiveUpdate", "LiveUpdateMonitor", "main"]
