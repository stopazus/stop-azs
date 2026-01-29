"""Telemetry and observability utilities."""

import time
from contextlib import contextmanager
from typing import Generator

from prometheus_client import Counter, Histogram, Gauge

# Metrics
sar_submissions_total = Counter(
    "sar_submissions_total",
    "Total number of SAR submission attempts",
    ["status"]
)

sar_submission_duration = Histogram(
    "sar_submission_duration_seconds",
    "SAR submission processing duration",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

validation_errors_total = Counter(
    "validation_errors_total",
    "Total number of validation errors"
)

database_operations = Histogram(
    "database_operation_duration_seconds",
    "Database operation duration",
    ["operation"]
)

active_requests = Gauge(
    "active_requests",
    "Number of requests currently being processed"
)


@contextmanager
def track_time(metric: Histogram, labels: dict = None) -> Generator:
    """
    Context manager to track operation duration.
    
    Args:
        metric: Prometheus histogram metric
        labels: Optional labels for the metric
    """
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        if labels:
            metric.labels(**labels).observe(duration)
        else:
            metric.observe(duration)
