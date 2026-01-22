"""Processing pipeline for SAR submissions with transactional storage.

The pipeline coordinates validation, logging, metrics, and database writes so
that downstream consumers never observe partially processed SAR submissions.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

from .instrumentation import MetricsRecorder, emit_log, emit_metric
from .validator import ValidationResult, validate_string


class TransactionManager(Protocol):
    """Protocol describing transactional semantics for data writes."""

    def begin(self) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...


class SARRepository(Protocol):
    """Persist validated SAR payloads inside a managed transaction."""

    def save(self, xml_text: str, correlation_id: str) -> None:
        ...


class TransactionContext:
    """Context manager that guarantees commit or rollback."""

    def __init__(self, manager: TransactionManager) -> None:
        self.manager = manager

    def __enter__(self) -> TransactionContext:
        self.manager.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is None:
            try:
                self.manager.commit()
            except Exception:
                self.manager.rollback()
                raise
        else:  # pragma: no cover - defensive guard
            self.manager.rollback()
        return False


@dataclass(slots=True)
class SARProcessor:
    """Validate SAR documents, then store them within an explicit transaction."""

    repository: SARRepository
    transactions: TransactionManager
    metrics: MetricsRecorder | None = None
    logger: logging.Logger | None = None

    def process(self, xml_text: str, correlation_id: str) -> ValidationResult:
        """Validate and persist a SAR submission.

        Logs and metrics emitted by this method include the ``correlation_id``
        so consumers can trace a single SAR across the gateway, application,
        validation, and database layers.
        """

        emit_log(
            self.logger,
            logging.INFO,
            "sar_request_received",
            correlation_id=correlation_id,
            stage="gateway",
        )
        emit_metric(
            self.metrics,
            "sar.request.received",
            correlation_id=correlation_id,
            stage="gateway",
        )

        validation = validate_string(
            xml_text,
            correlation_id=correlation_id,
            logger=self.logger,
            metrics=self.metrics,
        )

        if not validation.is_valid:
            emit_log(
                self.logger,
                logging.WARNING,
                "sar_request_rejected",
                correlation_id=correlation_id,
                stage="application",
                status="validation_failed",
            )
            emit_metric(
                self.metrics,
                "sar.request.rejected",
                correlation_id=correlation_id,
                stage="application",
                status="validation_failed",
            )
            return validation

        emit_log(
            self.logger,
            logging.INFO,
            "sar_request_validated",
            correlation_id=correlation_id,
            stage="application",
        )
        emit_metric(
            self.metrics,
            "sar.request.validated",
            correlation_id=correlation_id,
            stage="application",
        )

        try:
            with TransactionContext(self.transactions):
                emit_log(
                    self.logger,
                    logging.INFO,
                    "sar_transaction_started",
                    correlation_id=correlation_id,
                    stage="database",
                )
                emit_metric(
                    self.metrics,
                    "sar.storage.transaction_started",
                    correlation_id=correlation_id,
                    stage="database",
                )

                self.repository.save(xml_text, correlation_id)

                emit_log(
                    self.logger,
                    logging.INFO,
                    "sar_payload_saved",
                    correlation_id=correlation_id,
                    stage="database",
                )
                emit_metric(
                    self.metrics,
                    "sar.storage.saved",
                    correlation_id=correlation_id,
                    stage="database",
                )
        except Exception:
            emit_log(
                self.logger,
                logging.ERROR,
                "sar_transaction_rolled_back",
                correlation_id=correlation_id,
                stage="database",
            )
            emit_metric(
                self.metrics,
                "sar.storage.failed",
                correlation_id=correlation_id,
                stage="database",
            )
            raise

        emit_log(
            self.logger,
            logging.INFO,
            "sar_transaction_committed",
            correlation_id=correlation_id,
            stage="database",
        )
        emit_metric(
            self.metrics,
            "sar.storage.transaction_committed",
            correlation_id=correlation_id,
            stage="database",
        )
        emit_log(
            self.logger,
            logging.INFO,
            "sar_request_completed",
            correlation_id=correlation_id,
            stage="application",
        )
        emit_metric(
            self.metrics,
            "sar.request.completed",
            correlation_id=correlation_id,
            stage="application",
        )

        return validation


__all__ = [
    "SARProcessor",
    "SARRepository",
    "TransactionContext",
    "TransactionManager",
]
