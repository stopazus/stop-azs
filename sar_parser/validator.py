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

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Optional, Tuple, Union
import xml.etree.ElementTree as ET


# -- public data structures -------------------------------------------------


@dataclass(frozen=True)
class ValidationError:
    """Represents a single validation issue discovered in a SAR document."""

    message: str
    """Human-readable description of the issue."""

    xpath: str
    """Approximate XPath indicating the location of the issue."""

    severity: str = "error"
    """Severity level (``error`` or ``warning``)."""


@dataclass(frozen=True)
class ValidationResult:
    """Summary of the validation process."""

    errors: Tuple[ValidationError, ...]

    @property
    def is_valid(self) -> bool:
        """``True`` when no errors were reported."""

        return not self.errors

    def require_valid(self) -> None:
        """Raise a :class:`ValueError` if validation errors were encountered."""

        if self.errors:
            joined = "; ".join(error.message for error in self.errors)
            raise ValueError(f"SAR validation failed: {joined}")


# -- public API -------------------------------------------------------------


def validate_string(xml_content: Union[str, bytes]) -> ValidationResult:
    """Validate a SAR XML document provided as a string.

    Parameters
    ----------
    xml_content:
        Raw XML bytes or string.
    """

    root = _load_xml(xml_content)
    errors = tuple(_validate_root(root))
    return ValidationResult(errors=errors)


def validate_file(path: Union[str, Path]) -> ValidationResult:
    """Validate a SAR XML file on disk."""

    xml_bytes = Path(path).read_bytes()
    return validate_string(xml_bytes)


def validate_document(root: ET.Element) -> ValidationResult:
    """Validate an already-parsed :class:`~xml.etree.ElementTree.Element`."""

    root_copy = ET.fromstring(ET.tostring(root))
    _strip_namespaces(root_copy)
    errors = tuple(_validate_root(root_copy))
    return ValidationResult(errors=errors)


# -- validation helpers -----------------------------------------------------


PLACEHOLDER_VALUES = {"", "pending", "tbd", "unknown", "n/a"}
"""Values considered placeholders and therefore invalid for required fields."""


def _load_xml(xml_content: Union[str, bytes, Path]) -> ET.Element:
    """Load XML content from a string/bytes blob or a path."""

    if isinstance(xml_content, (str, bytes)):
        if isinstance(xml_content, str):
            potential_path = Path(xml_content)
            if potential_path.exists():
                data = potential_path.read_bytes()
            else:
                data = xml_content.encode("utf-8")
        else:
            data = xml_content
    else:
        data = Path(xml_content).read_bytes()

    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        message = f"Malformed XML: {exc}."
        raise ValueError(message) from exc

    _strip_namespaces(root)
    return root


def _strip_namespaces(element: ET.Element) -> None:
    """Remove namespace prefixes in-place to simplify traversal."""

    for el in element.iter():
        if not isinstance(el.tag, str):
            continue
        if el.tag.startswith("{"):
            el.tag = el.tag.split("}", 1)[1]
        attrib = el.attrib
        for key in list(attrib):
            if key.startswith("{"):
                new_key = key.split("}", 1)[1]
                attrib[new_key] = attrib.pop(key)


def _validate_root(root: ET.Element) -> Iterable[ValidationError]:
    if root.tag != "SAR":
        yield ValidationError("Root element must be <SAR>.", "/SAR")

    filing = root.find("FilingInformation")
    if filing is None:
        yield ValidationError("Missing <FilingInformation> block.", "/FilingInformation")
    else:
        yield from _validate_filing_information(filing)

    filer = root.find("FilerInformation")
    if filer is None:
        yield ValidationError("Missing <FilerInformation> block.", "/FilerInformation")
    else:
        yield from _validate_filer_information(filer)

    subjects = root.find("Subjects")
    if subjects is None:
        yield ValidationError("At least one <Subject> is required.", "/Subjects")
    else:
        subject_nodes = subjects.findall("Subject")
        if not subject_nodes:
            yield ValidationError("At least one <Subject> is required.", "/Subjects")
        else:
            for index, subject in enumerate(subject_nodes, start=1):
                yield from _validate_subject(subject, index)

    transactions = root.find("Transactions")
    if transactions is None:
        yield ValidationError("At least one <Transaction> is required.", "/Transactions")
    else:
        transaction_nodes = transactions.findall("Transaction")
        if not transaction_nodes:
            yield ValidationError("At least one <Transaction> is required.", "/Transactions")
        else:
            for index, transaction in enumerate(transaction_nodes, start=1):
                yield from _validate_transaction(transaction, index)


def _validate_filing_information(filing: ET.Element) -> Iterable[ValidationError]:
    path = "/FilingInformation"
    _, errors = _require_text(filing, "FilingType", f"{path}/FilingType")
    yield from errors

    filing_date_text, errors = _require_text(filing, "FilingDate", f"{path}/FilingDate")
    yield from errors
    if filing_date_text:
        try:
            datetime.strptime(filing_date_text, "%Y-%m-%d")
        except ValueError:
            yield ValidationError("FilingDate must be in YYYY-MM-DD format.", f"{path}/FilingDate")

    amendment = filing.findtext("AmendmentType")
    if amendment is None:
        yield ValidationError("Missing AmendmentType entry.", f"{path}/AmendmentType")


def _validate_filer_information(filer: ET.Element) -> Iterable[ValidationError]:
    base_path = "/FilerInformation"
    _, errors = _require_text(filer, "FilerName", f"{base_path}/FilerName")
    yield from errors

    address = filer.find("FilerAddress")
    if address is None:
        yield ValidationError("Missing filer address block.", f"{base_path}/FilerAddress")
    else:
        for tag in ("AddressLine1", "City", "State", "ZIP", "Country"):
            _, errors = _require_text(address, tag, f"{base_path}/FilerAddress/{tag}")
            yield from errors


def _validate_subject(subject: ET.Element, index: int) -> Iterable[ValidationError]:
    base_path = f"/Subjects/Subject[{index}]"
    _, errors = _require_text(subject, "Name", f"{base_path}/Name")
    yield from errors
    entity_type = subject.findtext("EntityType")
    if entity_type is None:
        yield ValidationError("Subject missing EntityType.", f"{base_path}/EntityType")


def _validate_transaction(transaction: ET.Element, index: int) -> Iterable[ValidationError]:
    base_path = f"/Transactions/Transaction[{index}]"

    tx_date_text, errors = _require_text(transaction, "Date", f"{base_path}/Date")
    yield from errors
    if tx_date_text:
        try:
            datetime.strptime(tx_date_text, "%Y-%m-%d")
        except ValueError:
            yield ValidationError("Transaction date must be in YYYY-MM-DD format.", f"{base_path}/Date")

    amount_element = transaction.find("Amount")
    if amount_element is None:
        yield ValidationError("Transaction missing Amount element.", f"{base_path}/Amount")
    else:
        currency = amount_element.attrib.get("currency")
        if not currency:
            yield ValidationError("Amount element missing currency attribute.", f"{base_path}/Amount/@currency")
        amount_text = _clean_text(amount_element.text)
        if _is_placeholder(amount_text):
            yield ValidationError("Amount must be provided instead of a placeholder.", f"{base_path}/Amount")
        elif amount_text:
            try:
                value = Decimal(amount_text)
            except InvalidOperation:
                yield ValidationError("Amount must be a valid decimal number.", f"{base_path}/Amount")
            else:
                if value <= 0:
                    yield ValidationError("Amount must be positive.", f"{base_path}/Amount")

    origin_account = transaction.find("OriginatingAccount")
    if origin_account is None:
        yield ValidationError("OriginatingAccount is required.", f"{base_path}/OriginatingAccount")
    else:
        _, errors = _require_text(origin_account, "Name", f"{base_path}/OriginatingAccount/Name")
        yield from errors

    beneficiaries_parent = transaction.find("Beneficiaries")
    if beneficiaries_parent is None:
        yield ValidationError("At least one Beneficiary is required.", f"{base_path}/Beneficiaries")
    else:
        beneficiaries = [
            _clean_text(node.text) for node in beneficiaries_parent.findall("Beneficiary")
        ]
        valid_beneficiaries = [value for value in beneficiaries if value]
        if not valid_beneficiaries:
            yield ValidationError("At least one Beneficiary is required.", f"{base_path}/Beneficiaries")
        else:
            for b_index, beneficiary in enumerate(valid_beneficiaries, start=1):
                if _is_placeholder(beneficiary):
                    yield ValidationError(
                        "Beneficiary must not be a placeholder value.",
                        f"{base_path}/Beneficiaries/Beneficiary[{b_index}]",
                    )

    uetr_text, errors = _require_text(transaction, "UETR", f"{base_path}/UETR")
    yield from errors
    if uetr_text:
        normalized = uetr_text.replace("-", "").strip()
        if len(normalized) != 32:
            yield ValidationError("UETR must be a 32 character hexadecimal value.", f"{base_path}/UETR")
        elif not all(char in "0123456789abcdefABCDEF" for char in normalized):
            yield ValidationError("UETR must be hexadecimal characters only.", f"{base_path}/UETR")


# -- primitive utilities ----------------------------------------------------


def _clean_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _is_placeholder(value: Optional[str]) -> bool:
    if value is None:
        return True
    return value.strip().lower() in PLACEHOLDER_VALUES


def _require_text(parent: ET.Element, tag: str, xpath: str) -> Tuple[Optional[str], Tuple[ValidationError, ...]]:
    child = parent.find(tag)
    if child is None:
        return None, (ValidationError(f"Missing <{tag}> element.", xpath),)

    text = _clean_text(child.text)
    if _is_placeholder(text):
        return None, (ValidationError(f"<{tag}> cannot be empty or a placeholder value.", xpath),)

    return text, ()
