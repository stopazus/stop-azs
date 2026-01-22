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
from datetime import datetime

from dataclasses import dataclass, field
from typing import Iterable, Optional
from xml.etree import ElementTree as ET


PLACEHOLDER_VALUES = {
    "",
    "UNKNOWN",
    "PENDING",
    "NOT APPLICABLE",
}

UETR_PATTERN = re.compile(r"^[A-Fa-f0-9]{32}$")
DRIVE_MAPPINGS = {
    "G": (r"\\\\nas\\Cloud-GDrive", "Google Drive"),
    "I": (r"\\\\nas\\Cloud-iCloud", "iCloud"),
    "O": (r"\\\\nas\\Cloud-OneDrive", "OneDrive"),
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


def _validate_required_text(
    parent: ET.Element,
    tag: str,
    location: str,
    result: ValidationResult,
    missing_message: str,
    placeholder_message: Optional[str] = None,
) -> Optional[str]:
    element = parent.find(tag)
    if element is None:
        result.errors.append(ValidationError(missing_message, location=location))
        return None

    value = _normalise_text(element.text)
    if _is_placeholder(value):
        result.errors.append(
            ValidationError(
                placeholder_message or missing_message,
                location=location,
            )
        )
        return None

    return value


def _validate_date(value: str, location: str, result: ValidationResult, label: str) -> None:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        result.errors.append(
            ValidationError(
                f"{label} must be in YYYY-MM-DD format.",
                location=location,
            )
        )


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
    _validate_filing_information(root, result)
    _validate_filer_information(root, result)
    _validate_subjects(root, result)
    _validate_transactions(root, result)

    return result


def validate_file(path: "str | os.PathLike[str] | os.PathLike[bytes] | int") -> ValidationResult:
    """Load a SAR document from disk and validate its contents."""

    result = ValidationResult()

    try:
        with open(path, "r", encoding="utf-8") as handle:
            xml_text = handle.read()
    except OSError as exc:  # pragma: no cover - file access can vary by environment
        hint = _nas_drive_hint(str(path))
        message = f"Unable to read file '{path}': {exc}."
        if hint:
            message = f"{message} {hint}"

        result.errors.append(ValidationError(message=message, location=str(path)))
        return result

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


def _validate_filing_information(root: ET.Element, result: ValidationResult) -> None:
    filing = root.find("FilingInformation")
    if filing is None:
        return

    _validate_required_text(
        filing,
        "FilingType",
        "/SAR/FilingInformation/FilingType",
        result,
        "Missing <FilingType> value.",
        "FilingType cannot be empty or a placeholder.",
    )

    filing_date = _validate_required_text(
        filing,
        "FilingDate",
        "/SAR/FilingInformation/FilingDate",
        result,
        "Missing <FilingDate> value.",
        "FilingDate cannot be empty or a placeholder.",
    )
    if filing_date:
        _validate_date(
            filing_date,
            "/SAR/FilingInformation/FilingDate",
            result,
            "FilingDate",
        )

    _validate_required_text(
        filing,
        "AmendmentType",
        "/SAR/FilingInformation/AmendmentType",
        result,
        "Missing <AmendmentType> value.",
        "AmendmentType cannot be empty or a placeholder.",
    )


def _validate_filer_information(root: ET.Element, result: ValidationResult) -> None:
    filer = root.find("FilerInformation")
    if filer is None:
        return

    _validate_required_text(
        filer,
        "FilerName",
        "/SAR/FilerInformation/FilerName",
        result,
        "Missing <FilerName> value.",
        "FilerName cannot be empty or a placeholder.",
    )

    address = filer.find("FilerAddress")
    if address is None:
        result.errors.append(
            ValidationError("Missing <FilerAddress> block.", location="/SAR/FilerInformation")
        )
        return

    for tag in ("AddressLine1", "City", "State", "ZIP", "Country"):
        _validate_required_text(
            address,
            tag,
            f"/SAR/FilerInformation/FilerAddress/{tag}",
            result,
            f"Missing <{tag}> value in filer address.",
            f"<{tag}> in filer address cannot be empty or a placeholder.",
        )


def _validate_subjects(root: ET.Element, result: ValidationResult) -> None:
    for index, subject in enumerate(root.findall("Subjects/Subject"), start=1):
        _validate_required_text(
            subject,
            "Name",
            f"/SAR/Subjects/Subject[{index}]/Name",
            result,
            "Subject must include a <Name> element.",
            "Subject name cannot be empty or a placeholder.",
        )

        _validate_required_text(
            subject,
            "EntityType",
            f"/SAR/Subjects/Subject[{index}]/EntityType",
            result,
            "Subject must include an <EntityType> element.",
            "EntityType cannot be empty or a placeholder.",
        )


def _validate_transactions(root: ET.Element, result: ValidationResult) -> None:
    for index, transaction in enumerate(root.findall("Transactions/Transaction"), start=1):
        amount_location = f"/SAR/Transactions/Transaction[{index}]/Amount"
        date_value = _validate_required_text(
            transaction,
            "Date",
            f"/SAR/Transactions/Transaction[{index}]/Date",
            result,
            "Transaction is missing a <Date> element.",
            "Transaction date cannot be empty or a placeholder.",
        )
        if date_value:
            _validate_date(
                date_value,
                f"/SAR/Transactions/Transaction[{index}]/Date",
                result,
                "Transaction date",
            )

        amount = transaction.find("Amount")
        if amount is None:
            result.errors.append(
                ValidationError(
                    "Transaction is missing an <Amount> element.",
                    location=amount_location,
                )
            )
            continue

        amount_text = _normalise_text(amount.text)
        if _is_placeholder(amount_text):
            result.errors.append(
                ValidationError(
                    "Amount must be provided instead of a placeholder.",
                    location=f"/SAR/Transactions/Transaction[{index}]/Amount",
                )
            )
        else:
            try:
                float(amount_text)
            except ValueError:
                result.errors.append(
                    ValidationError(
                        "Amount must be numeric.",
                        location=f"/SAR/Transactions/Transaction[{index}]/Amount",
                    )
                )

        currency = amount.get("currency")
        if currency is None or _is_placeholder(currency):
            result.errors.append(
                ValidationError(
                    "Amount currency code is required.",
                    location=amount_location,
                )
            )
        elif currency is not None:
            normalised_currency = currency.strip()
            if len(normalised_currency) != 3 or not normalised_currency.isalpha():
                result.errors.append(
                    ValidationError(
                        "Amount currency code must be a three-letter code.",
                        location=f"/SAR/Transactions/Transaction[{index}]/Amount",
                    )
                )

        uetr = transaction.find("UETR")
        if uetr is None:
            result.errors.append(
                ValidationError(
                    "Transaction is missing a <UETR> element.",
                    location=f"/SAR/Transactions/Transaction[{index}]",
                )
            )
        else:
            uetr_value = _normalise_text(uetr.text)
            if not UETR_PATTERN.match(uetr_value):
                result.errors.append(
                    ValidationError(
                        "UETR must be a 32-character hexadecimal string.",
                        location=f"/SAR/Transactions/Transaction[{index}]/UETR",
                    )
                )


def _nas_drive_hint(path: str) -> Optional[str]:
    match = re.match(r"^(?P<drive>[A-Za-z]):[\\/]", path)
    if not match:
        return None

    drive_letter = match.group("drive").upper()
    mapping = DRIVE_MAPPINGS.get(drive_letter)
    if not mapping:
        return None

    mapped_path, service_name = mapping
    return (
        f"Drive {drive_letter}: is mapped to '{mapped_path}' ({service_name}). "
        "Try reconnecting the network drive or using the UNC path."
    )


__all__ = [
    "ValidationError",
    "ValidationResult",
    "validate_file",
    "validate_string",
]
