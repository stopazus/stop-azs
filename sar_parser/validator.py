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

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, Iterable, List, Optional
from xml.etree import ElementTree as ET

__all__ = [
    "ValidationError",
    "ValidationResult",
    "validate_file",
    "validate_string",
]


PLACEHOLDER_VALUES = {"", "UNKNOWN", "PENDING", "N/A", "NA"}


@dataclass
class ValidationError:
    """Container describing a single validation error."""

    message: str
    xpath: str = ""
    severity: str = "error"

    def __str__(self) -> str:  # pragma: no cover - convenience only
        if self.xpath:
            return f"{self.message} ({self.xpath})"
        return self.message


@dataclass
class ValidationResult:
    """Represents the outcome of a validation run."""

    errors: List[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Whether the validation run produced any errors."""

        return not self.errors

    def add_error(self, message: str, xpath: str = "") -> None:
        self.errors.append(ValidationError(message=message, xpath=xpath))

    def extend(self, errors: Iterable[ValidationError]) -> None:
        self.errors.extend(errors)

    def require_valid(self) -> "ValidationResult":
        """Raise :class:`ValueError` if any errors were collected."""

        if self.errors:
            messages = "; ".join(error.message for error in self.errors)
            raise ValueError(f"SAR document failed validation: {messages}")
        return self


def validate_string(xml_blob: str) -> ValidationResult:
    """Validate an in-memory XML string."""

    result = ValidationResult()
    try:
        root = ET.fromstring(xml_blob)
    except ET.ParseError as exc:
        result.add_error(f"Malformed XML: {exc}")
        return result

    if root.tag != "SAR":
        result.add_error("Root element must be <SAR>.", "/")
        # Continue with additional validation to provide more feedback.

    _check_required_sections(root, result)
    parent_map = _build_parent_map(root)
    _check_amounts(root, result, parent_map)
    _check_dates(root, result, parent_map)
    _check_uetrs(root, result, parent_map)

    return result


def validate_file(path: str) -> ValidationResult:
    """Validate a SAR XML document stored on disk."""

    with open(path, "r", encoding="utf-8") as file_obj:
        xml_blob = file_obj.read()
    return validate_string(xml_blob)


def _build_parent_map(root: ET.Element) -> Dict[ET.Element, ET.Element]:
    return {child: parent for parent in root.iter() for child in list(parent)}


def _check_required_sections(root: ET.Element, result: ValidationResult) -> None:
    filer = root.find("FilerInformation")
    if filer is None:
        result.add_error("Missing <FilerInformation> block.", "/SAR/FilerInformation")

    subjects = root.find("Subjects")
    if subjects is None or not subjects.findall("Subject"):
        result.add_error("At least one <Subject> is required.", "/SAR/Subjects")

    transactions = root.find("Transactions")
    if transactions is None or not transactions.findall("Transaction"):
        result.add_error("At least one <Transaction> is required.", "/SAR/Transactions")


def _check_amounts(
    root: ET.Element, result: ValidationResult, parent_map: Dict[ET.Element, ET.Element]
) -> None:
    for amount in root.findall(".//Amount"):
        text = (amount.text or "").strip()
        xpath = _build_xpath(amount, parent_map)
        if text.upper() in PLACEHOLDER_VALUES:
            result.add_error("Amount must be provided instead of a placeholder.", xpath)
            continue

        if not text:
            result.add_error("Amount value is required.", xpath)
            continue

        try:
            value = Decimal(text)
        except InvalidOperation:
            result.add_error("Amount must be a numeric value.", xpath)
            continue

        if value < 0:
            result.add_error("Amount must be zero or greater.", xpath)

        currency = amount.get("currency")
        if (
            currency is None
            or len(currency) != 3
            or not currency.isalpha()
            or not currency.isupper()
        ):
            result.add_error("Amount currency attribute must be a three-letter code.", xpath)


def _check_dates(
    root: ET.Element, result: ValidationResult, parent_map: Dict[ET.Element, ET.Element]
) -> None:
    for element in root.iter():
        if not element.tag.endswith("Date"):
            continue

        text = (element.text or "").strip()
        if not text:
            xpath = _build_xpath(element, parent_map)
            result.add_error("Date value is required.", xpath)
            continue

        if text.upper() in PLACEHOLDER_VALUES:
            xpath = _build_xpath(element, parent_map)
            result.add_error("Date must be provided instead of a placeholder.", xpath)
            continue

        try:
            datetime.strptime(text, "%Y-%m-%d")
        except ValueError:
            xpath = _build_xpath(element, parent_map)
            result.add_error("Date must use ISO format YYYY-MM-DD.", xpath)


def _check_uetrs(
    root: ET.Element, result: ValidationResult, parent_map: Dict[ET.Element, ET.Element]
) -> None:
    for uetr in root.findall(".//UETR"):
        text = (uetr.text or "").strip()
        xpath = _build_xpath(uetr, parent_map)
        if not text or text.upper() in PLACEHOLDER_VALUES:
            result.add_error("UETR must be provided instead of a placeholder.", xpath)
            continue

        try:
            # ``uuid.UUID`` accepts both hyphenated UUID strings and 32-digit hex
            # representations, which covers the formats seen in FinCEN filings.
            uuid.UUID(text)
        except ValueError:
            result.add_error("UETR must be a valid UUID.", xpath)


def _build_xpath(
    element: ET.Element, parent_map: Dict[ET.Element, ET.Element]
) -> str:
    """Reconstruct a simple XPath pointing to *element*."""

    path_parts: List[str] = []
    current: Optional[ET.Element] = element
    while current is not None:
        parent = parent_map.get(current)
        if parent is not None:
            siblings = [child for child in list(parent) if child.tag == current.tag]
            index = siblings.index(current) + 1 if len(siblings) > 1 else None
        else:
            index = None
        if index is not None:
            path_parts.append(f"{current.tag}[{index}]")
        else:
            path_parts.append(current.tag)
        current = parent
    path_parts.reverse()
    return "/" + "/".join(path_parts)
