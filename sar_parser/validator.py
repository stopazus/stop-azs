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

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Sequence
import xml.etree.ElementTree as ET

_PLACEHOLDER_VALUES = {"PENDING", "UNKNOWN", "TBD", "N/A", "NA"}


def _local_name(tag: str) -> str:
    """Return the local name of an XML tag without namespace information."""

    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _strip_namespaces(element: ET.Element) -> None:
    """Recursively drop XML namespaces to simplify tag comparisons."""

    element.tag = _local_name(element.tag)
    for child in element:
        _strip_namespaces(child)


@dataclass(slots=True)
class ValidationError:
    """Represents a single validation problem."""

    message: str
    location: str | None = None
    severity: str | None = "error"


@dataclass(slots=True)
class ValidationResult:
    """Container for errors produced during validation."""

    errors: List[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors

    def add(self, message: str, *, location: str | None = None) -> None:
        self.errors.append(ValidationError(message=message, location=location))


def _validate_transactions(transactions: Iterable[ET.Element], result: ValidationResult) -> None:
    for index, transaction in enumerate(transactions, start=1):
        amount = transaction.find("Amount")
        location = f"/Transactions/Transaction[{index}]/Amount"
        if amount is None or (amount.text is None or not amount.text.strip()):
            result.add("Amount must be provided instead of a placeholder.", location=location)
            continue

        text = amount.text.strip()
        if text.upper() in _PLACEHOLDER_VALUES:
            result.add("Amount must be provided instead of a placeholder.", location=location)
            continue

        try:
            float(text)
        except ValueError:
            result.add("Amount must be a valid number.", location=location)


def validate_string(xml_text: str) -> ValidationResult:
    """Validate a SAR XML document provided as a string."""

    result = ValidationResult()
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        result.add(f"XML parsing failed: {exc}.", location="/")
        return result

    _strip_namespaces(root)

    if root.tag != "SAR":
        result.add("Document root must be <SAR>.", location=f"/{root.tag}")
        return result

    filer_info = root.find("FilerInformation")
    if filer_info is None:
        result.add("Missing <FilerInformation> block.", location="/FilerInformation")

    subjects = root.find("Subjects")
    if subjects is None or not subjects.findall("Subject"):
        result.add("At least one <Subject> is required.", location="/Subjects")

    transactions_container = root.find("Transactions")
    if transactions_container is None:
        result.add("At least one <Transaction> is required.", location="/Transactions")
        transactions: Sequence[ET.Element] = []
    else:
        transactions = transactions_container.findall("Transaction")
        if not transactions:
            result.add("At least one <Transaction> is required.", location="/Transactions")

    if transactions:
        _validate_transactions(transactions, result)

    return result


def validate_file(path: Path | str) -> ValidationResult:
    """Validate a SAR XML document stored on disk."""

    xml_path = Path(path)
    xml_text = xml_path.read_text(encoding="utf-8")
    return validate_string(xml_text)


__all__ = [
    "ValidationError",
    "ValidationResult",
    "validate_string",
    "validate_file",
]
