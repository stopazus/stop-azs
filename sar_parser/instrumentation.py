"""Shared helpers for emitting structured logs and metrics events.

The helpers avoid optional dependencies while encouraging consistent
correlation ID handling across validation and storage workflows.
"""

from __future__ import annotations

import logging
from typing import Protocol


class MetricsRecorder(Protocol):
    """Protocol describing a minimal metrics recording interface."""

    def record(
        self,
        name: str,
        value: float = 1.0,
        *,
        correlation_id: str | None = None,
        **labels: str,
    ) -> None:
        ...


def emit_log(
    logger: logging.Logger | None,
    level: int,
    message: str,
    *,
    correlation_id: str | None = None,
    **fields: str,
) -> None:
    """Send a structured log event if a logger is available."""

    if logger is None:
        return

    extra = dict(fields)
    if correlation_id is not None:
        extra["correlation_id"] = correlation_id
    logger.log(level, message, extra=extra)


def emit_metric(
    metrics: MetricsRecorder | None,
    name: str,
    *,
    correlation_id: str | None = None,
    value: float = 1.0,
    **labels: str,
) -> None:
    """Record a metrics datapoint if a recorder is provided."""

    if metrics is None:
        return

    metrics.record(name, value, correlation_id=correlation_id, **labels)


__all__ = ["emit_log", "emit_metric", "MetricsRecorder"]
