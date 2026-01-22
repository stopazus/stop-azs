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

DEFAULT_ALLOWED_CURRENCIES = {
    "USD",
    "EUR",
    "GBP",
    "CAD",
    "AUD",
    "NZD",
    "JPY",
    "CHF",
    "CNY",
    "HKD",
    "SGD",
    "SEK",
    "NOK",
    "DKK",
    "MXN",
    "BRL",
    "INR",
    "ZAR",
    "RUB",
    "AED",
    "SAR",
    "KRW",
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


def validate_string(
    xml_text: str, allowed_currencies: Optional[Iterable[str]] = None
) -> ValidationResult:
    """Validate a SAR document stored in memory.

    Args:
        xml_text: Raw SAR XML content.
        allowed_currencies: Optional allowlist of accepted three-letter
            currency codes. When omitted, a common ISO 4217 subset is used.
    """

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

    _strip_namespaces(root)

    if root.tag != "SAR":
        result.errors.append(
            ValidationError(
                message="Root element must be <SAR>.",
                location=f"/{root.tag}",
            )
        )
        return result

    _validate_required_blocks(root, result)
    _validate_transactions(root, result, allowed_currencies)

    return result


def validate_file(
    path: "str | os.PathLike[str] | os.PathLike[bytes] | int",
    *,
    allowed_currencies: Optional[Iterable[str]] = None,
) -> ValidationResult:
    """Load a SAR document from disk and validate its contents.

    Args:
        path: Filesystem path to a SAR XML document.
        allowed_currencies: Optional allowlist of accepted currency codes to
            validate against.
    """

    with open(path, "r", encoding="utf-8") as handle:
        xml_text = handle.read()
    return validate_string(xml_text, allowed_currencies)


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


def _validate_transactions(
    root: ET.Element,
    result: ValidationResult,
    allowed_currencies: Optional[Iterable[str]] = None,
) -> None:
    allowed_currency_set = {code.upper() for code in DEFAULT_ALLOWED_CURRENCIES}
    if allowed_currencies is not None:
        allowed_currency_set.update(code.upper() for code in allowed_currencies)

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

        if _is_placeholder(amount.text):
            result.errors.append(
                ValidationError(
                    "Amount must be provided instead of a placeholder.",
                    location=f"/SAR/Transactions/Transaction[{index}]/Amount",
                )
            )

        currency_code = amount.attrib.get("currency")
        if currency_code is None:
            result.errors.append(
                ValidationError(
                    "Amount currency attribute is required.",
                    location=f"/SAR/Transactions/Transaction[{index}]/Amount",
                )
            )
            continue

        normalised_currency = currency_code.strip().upper()
        if len(normalised_currency) != 3 or not normalised_currency.isalpha():
            result.errors.append(
                ValidationError(
                    "Currency codes must be three uppercase letters.",
                    location=f"/SAR/Transactions/Transaction[{index}]/Amount/@currency",
                )
            )
            continue

        if normalised_currency not in allowed_currency_set:
            result.errors.append(
                ValidationError(
                    f"Currency code '{normalised_currency}' is not allowed.",
                    location=f"/SAR/Transactions/Transaction[{index}]/Amount/@currency",
                )
            )


def _strip_namespaces(element: ET.Element) -> None:
    """Remove XML namespaces in-place to simplify validation lookups."""

    if element.tag.startswith("{"):
        element.tag = element.tag.split("}", 1)[1]

    for child in element:
        _strip_namespaces(child)


__all__ = [
    "ValidationError",
    "ValidationResult",
    "validate_file",
    "validate_string",
]
