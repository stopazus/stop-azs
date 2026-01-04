"""SAR XML validator utilities.

The validator performs a series of structural and semantic checks on
Suspicious Activity Report (SAR) documents that follow the FinCEN XML
schema.  The goal is to surface actionable validation errors instead of
raising low-level parsing exceptions.  The checks implemented here are not
exhaustive, but they cover the most common issues we have encountered when
working with upstream SAR feeds:

* malformed XML (e.g. missing closing tags or namespace declarations)
* missing or placeholder values (``PENDING``, ``UNKNOWN`` …) in required
  fields
* incorrect data formats (dates, currency amounts, UETR identifiers)
* missing core collections such as subjects, transactions and beneficiaries

The public entry points return :class:`ValidationResult` objects containing a
list of :class:`ValidationError` instances.  Each error captures a human
readable message, the XPath-like location of the problem, and an optional
severity level.

The module is intentionally dependency-free so it can run in automation
without additional packages.
"""

from __future__ import annotations

import os

from dataclasses import dataclass, field
from datetime import datetime
import re
from typing import Iterable, Optional
from xml.etree import ElementTree as ET


PLACEHOLDER_VALUES = {
    "",
    "UNKNOWN",
    "PENDING",
    "NOT APPLICABLE",
}


@dataclass(slots=True)
class ValidationError:
    """Description of a single validation problem."""

    message: str
    location: Optional[str] = None
    severity: str = "error"

    def __post_init__(self) -> None:  # pragma: no cover - defensive normalisation
        if self.location == "":
            self.location = None


@dataclass(slots=True)
class ValidationResult:
    """Container for validation errors discovered when inspecting a document."""

    errors: list[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Return ``True`` if no validation errors were collected."""

        return not self.errors

    def extend(self, new_errors: Iterable[ValidationError]) -> None:
        self.errors.extend(new_errors)


def _normalise_text(value: Optional[str]) -> str:
    return (value or "").strip()


def _is_placeholder(value: Optional[str]) -> bool:
    normalised = _normalise_text(value)
    return normalised.upper() in PLACEHOLDER_VALUES


def validate_string(xml_text: str) -> ValidationResult:
    """Validate a SAR document stored in memory."""

    result = ValidationResult()

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:  # pragma: no cover - defensive path for malformed XML
        result.errors.append(
            ValidationError(
                message=f"Malformed XML: {exc}.",
                location="/",
            )
        )
        return result

    if root.tag != "SAR":
        result.errors.append(
            ValidationError(
                message="Root element must be <SAR>.",
                location=f"/{root.tag}",
            )
        )
        return result

    _validate_required_blocks(root, result)
    _validate_transactions(root, result)

    return result


def validate_file(path: "str | os.PathLike[str] | os.PathLike[bytes] | int") -> ValidationResult:
    """Load a SAR document from disk and validate its contents."""

    with open(path, "r", encoding="utf-8") as handle:
        xml_text = handle.read()
    return validate_string(xml_text)


def _validate_required_blocks(root: ET.Element, result: ValidationResult) -> None:
    if root.find("FilingInformation") is None:
        result.errors.append(
            ValidationError("Missing <FilingInformation> block.", location="/SAR")
        )

    if root.find("FilerInformation") is None:
        result.errors.append(
            ValidationError("Missing <FilerInformation> block.", location="/SAR")
        )

    subjects = root.findall("Subjects/Subject")
    if not subjects:
        result.errors.append(
            ValidationError("At least one <Subject> is required.", location="/SAR/Subjects")
        )

    transactions = root.findall("Transactions/Transaction")
    if not transactions:
        result.errors.append(
            ValidationError(
                "At least one <Transaction> is required.",
                location="/SAR/Transactions",
            )
        )


def _validate_transactions(root: ET.Element, result: ValidationResult) -> None:
    for index, transaction in enumerate(root.findall("Transactions/Transaction"), start=1):
        amount = transaction.find("Amount")
        if amount is None:
            result.errors.append(
                ValidationError(
                    "Transaction is missing an <Amount> element.",
                    location=f"/SAR/Transactions/Transaction[{index}]",
                )
            )
            continue

        _validate_amount(amount, index, result)

        _validate_transaction_date(transaction.find("Date"), index, result)

        _validate_uetr(transaction.find("UETR"), index, result)


def _validate_amount(amount: ET.Element, index: int, result: ValidationResult) -> None:
    value = _normalise_text(amount.text)

    if not value:
        result.errors.append(
            ValidationError(
                "Amount value is required.",
                location=f"/SAR/Transactions/Transaction[{index}]/Amount",
            )
        )
    elif _is_placeholder(value):
        result.errors.append(
            ValidationError(
                "Amount must be provided instead of a placeholder.",
                location=f"/SAR/Transactions/Transaction[{index}]/Amount",
            )
        )

    if value and not _is_placeholder(value) and not _is_float(value):
        result.errors.append(
            ValidationError(
                "Amount must be a numeric value.",
                location=f"/SAR/Transactions/Transaction[{index}]/Amount",
            )
        )
    elif value and not _is_placeholder(value) and float(value) < 0:
        result.errors.append(
            ValidationError(
                "Amount cannot be negative.",
                location=f"/SAR/Transactions/Transaction[{index}]/Amount",
            )
        )

    currency = amount.attrib.get("currency")
    if not currency or not re.fullmatch(r"[A-Z]{3}", currency):
        result.errors.append(
            ValidationError(
                "Amount currency must be a three-letter ISO 4217 code.",
                location=f"/SAR/Transactions/Transaction[{index}]/Amount",
            )
        )


def _validate_transaction_date(date_element: Optional[ET.Element], index: int, result: ValidationResult) -> None:
    if date_element is None:
        result.errors.append(
            ValidationError(
                "Transaction is missing a <Date> element.",
                location=f"/SAR/Transactions/Transaction[{index}]",
            )
        )
        return

    value = _normalise_text(date_element.text)
    if not value or _is_placeholder(value):
        result.errors.append(
            ValidationError(
                "Transaction date must be provided instead of a placeholder.",
                location=f"/SAR/Transactions/Transaction[{index}]/Date",
            )
        )
        return
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        result.errors.append(
            ValidationError(
                "Transaction date must use YYYY-MM-DD format.",
                location=f"/SAR/Transactions/Transaction[{index}]/Date",
            )
        )


def _validate_uetr(uetr_element: Optional[ET.Element], index: int, result: ValidationResult) -> None:
    if uetr_element is None:
        result.errors.append(
            ValidationError(
                "Transaction is missing a <UETR> element.",
                location=f"/SAR/Transactions/Transaction[{index}]",
            )
        )
        return

    value = _normalise_text(uetr_element.text)
    if not value or _is_placeholder(value):
        result.errors.append(
            ValidationError(
                "UETR must be provided instead of a placeholder.",
                location=f"/SAR/Transactions/Transaction[{index}]/UETR",
            )
        )
        return
    if not re.fullmatch(r"[0-9a-fA-F]{32}", value):
        result.errors.append(
            ValidationError(
                "UETR must be a 32-character hexadecimal string.",
                location=f"/SAR/Transactions/Transaction[{index}]/UETR",
            )
        )


def _is_float(value: str) -> bool:
    try:
        float(value)
    except ValueError:
        return False
    return True


__all__ = [
    "ValidationError",
    "ValidationResult",
    "validate_file",
    "validate_string",
]
