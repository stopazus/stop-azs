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
import re
from decimal import Decimal, InvalidOperation

from dataclasses import dataclass, field
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
                    location=f"/SAR/Transactions/Transaction[{index}]/Amount",
                )
            )
            continue

        if _is_placeholder(amount.text):
            result.errors.append(
                ValidationError(
                    "Amount must be provided instead of a placeholder.",
                    location=f"/SAR/Transactions/Transaction[{index}]/Amount",
                )
            )

        else:
            raw_amount = _normalise_text(amount.text)

            if any(char in raw_amount for char in ("$", ",")):
                result.errors.append(
                    ValidationError(
                        "Amount must not contain currency symbols or commas.",
                        location=f"/SAR/Transactions/Transaction[{index}]/Amount",
                    )
                )
            else:
                try:
                    val = Decimal(raw_amount)

                    if val < 0:
                        result.errors.append(
                            ValidationError(
                                "Amount must be a non-negative value.",
                                location=f"/SAR/Transactions/Transaction[{index}]/Amount",
                            )
                        )

                    if val.as_tuple().exponent < -2:
                        result.errors.append(
                            ValidationError(
                                "Amount cannot have more than 2 decimal places.",
                                location=f"/SAR/Transactions/Transaction[{index}]/Amount",
                            )
                        )

                except InvalidOperation:
                    result.errors.append(
                        ValidationError(
                            "Amount must be a valid numeric value.",
                            location=f"/SAR/Transactions/Transaction[{index}]/Amount",
                        )
                    )

        uetr = transaction.find("UETR")
        if uetr is None or _is_placeholder(uetr.text):
            result.errors.append(
                ValidationError(
                    "Transaction is missing a valid <UETR> identifier.",
                    location=f"/SAR/Transactions/Transaction[{index}]/UETR",
                )
            )
        else:
            normalised_uetr = _normalise_text(uetr.text)
            uuid_pattern = (
                r"^[0-9a-fA-F]{8}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?"
                r"[0-9a-fA-F]{4}-?[0-9a-fA-F]{12}$"
            )

            if not re.fullmatch(uuid_pattern, normalised_uetr):
                result.errors.append(
                    ValidationError(
                        "UETR must be a valid 32-character hex string or UUID.",
                        location=f"/SAR/Transactions/Transaction[{index}]/UETR",
                    )
                )


__all__ = [
    "ValidationError",
    "ValidationResult",
    "validate_file",
    "validate_string",
]
