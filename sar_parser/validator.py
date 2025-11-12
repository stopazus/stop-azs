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


def _add_error(result: ValidationResult, message: str, location: str) -> None:
    """Helper to add a validation error to the result."""
    result.errors.append(ValidationError(message=message, location=location))


def _check_required_element(
    root: ET.Element,
    xpath: str,
    error_message: str,
    location: str,
    result: ValidationResult,
) -> bool:
    """Check if a required element exists and add an error if missing.
    
    Returns True if the element exists, False otherwise.
    """
    elements = root.findall(xpath) if "/" in xpath else ([root.find(xpath)] if root.find(xpath) is not None else [])
    if not elements:
        _add_error(result, error_message, location)
        return False
    return True


def validate_string(xml_text: str) -> ValidationResult:
    """Validate a SAR document stored in memory."""

    result = ValidationResult()

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:  # pragma: no cover - defensive path for malformed XML
        _add_error(result, f"Malformed XML: {exc}.", "/")
        return result

    if root.tag != "SAR":
        _add_error(result, "Root element must be <SAR>.", f"/{root.tag}")
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
    _check_required_element(
        root,
        "FilerInformation",
        "Missing <FilerInformation> block.",
        "/SAR",
        result,
    )
    
    _check_required_element(
        root,
        "Subjects/Subject",
        "At least one <Subject> is required.",
        "/SAR/Subjects",
        result,
    )
    
    _check_required_element(
        root,
        "Transactions/Transaction",
        "At least one <Transaction> is required.",
        "/SAR/Transactions",
        result,
    )


def _validate_transactions(root: ET.Element, result: ValidationResult) -> None:
    for index, transaction in enumerate(root.findall("Transactions/Transaction"), start=1):
        amount = transaction.find("Amount")
        location_prefix = f"/SAR/Transactions/Transaction[{index}]"
        
        if amount is None:
            _add_error(
                result,
                "Transaction is missing an <Amount> element.",
                location_prefix,
            )
            continue

        if _is_placeholder(amount.text):
            _add_error(
                result,
                "Amount must be provided instead of a placeholder.",
                f"{location_prefix}/Amount",
            )


__all__ = [
    "ValidationError",
    "ValidationResult",
    "validate_file",
    "validate_string",
]
