"""Validation logic for SAR XML filings."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, List, Optional
import re
import xml.etree.ElementTree as ET


@dataclass
class ValidationIssue:
    """Represents a validation issue discovered in a SAR filing."""

    code: str
    message: str
    severity: str
    context: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "context": self.context,
        }


PLACEHOLDER_VALUES = {"pending", "tbd", "unknown", "n/a", "na"}


class SarValidator:
    """Validate Suspicious Activity Report (SAR) XML files."""

    def __init__(self, today: Optional[date] = None) -> None:
        self.today = today or date.today()

    def validate_file(self, path: Path) -> List[ValidationIssue]:
        """Validate a SAR file and return a list of issues."""
        issues: List[ValidationIssue] = []

        try:
            tree = ET.parse(path)
        except ET.ParseError as exc:
            issues.append(
                ValidationIssue(
                    code="malformed_xml",
                    message=f"XML parsing failed: {exc}",
                    severity="error",
                )
            )
            return issues

        root = tree.getroot()
        ns = self._namespace(root)

        issues.extend(self._check_filing_information(root, ns))
        issues.extend(self._check_transactions(root, ns))
        issues.extend(self._check_uetr(root, ns))

        return issues

    def _check_filing_information(self, root: ET.Element, ns: dict) -> Iterable[ValidationIssue]:
        issues: List[ValidationIssue] = []
        filing_date_text = self._find_text(root, ".//ns:FilingInformation/ns:FilingDate", ns)
        if filing_date_text:
            parsed = self._parse_iso_date(filing_date_text)
            if parsed is None:
                issues.append(
                    ValidationIssue(
                        code="invalid_filing_date",
                        message=f"FilingDate '{filing_date_text}' is not a valid ISO-8601 date.",
                        severity="error",
                        context="FilingInformation/FilingDate",
                    )
                )
            elif parsed > self.today:
                issues.append(
                    ValidationIssue(
                        code="future_filing_date",
                        message=f"FilingDate {filing_date_text} occurs in the future relative to today ({self.today.isoformat()}).",
                        severity="warning",
                        context="FilingInformation/FilingDate",
                    )
                )
        else:
            issues.append(
                ValidationIssue(
                    code="missing_filing_date",
                    message="FilingDate element is missing from FilingInformation.",
                    severity="error",
                    context="FilingInformation/FilingDate",
                )
            )
        return issues

    def _check_transactions(self, root: ET.Element, ns: dict) -> Iterable[ValidationIssue]:
        issues: List[ValidationIssue] = []
        for txn in root.findall(".//ns:Transaction", ns):
            date_text = self._find_text(txn, "ns:Date", ns)
            if date_text:
                parsed = self._parse_iso_date(date_text)
                if parsed is None:
                    issues.append(
                        ValidationIssue(
                            code="invalid_transaction_date",
                            message=f"Transaction date '{date_text}' is not a valid ISO-8601 date.",
                            severity="error",
                            context="Transactions/Transaction/Date",
                        )
                    )
                elif parsed > self.today:
                    issues.append(
                        ValidationIssue(
                            code="future_transaction_date",
                            message=f"Transaction date {date_text} occurs in the future relative to today ({self.today.isoformat()}).",
                            severity="warning",
                            context="Transactions/Transaction/Date",
                        )
                    )
            amount_element = txn.find("ns:Amount", ns)
            if amount_element is not None:
                amount_text = (amount_element.text or "").strip()
                if not amount_text:
                    issues.append(
                        ValidationIssue(
                            code="missing_amount",
                            message="Transaction amount is missing a value.",
                            severity="error",
                            context="Transactions/Transaction/Amount",
                        )
                    )
                elif amount_text.lower() in PLACEHOLDER_VALUES:
                    issues.append(
                        ValidationIssue(
                            code="placeholder_amount",
                            message=f"Transaction amount contains placeholder value '{amount_text}'.",
                            severity="error",
                            context="Transactions/Transaction/Amount",
                        )
                    )
                else:
                    if not self._is_positive_decimal(amount_text):
                        issues.append(
                            ValidationIssue(
                                code="invalid_amount",
                                message=f"Transaction amount '{amount_text}' is not a valid positive decimal.",
                                severity="error",
                                context="Transactions/Transaction/Amount",
                            )
                        )
            else:
                issues.append(
                    ValidationIssue(
                        code="missing_amount_element",
                        message="Transaction is missing Amount element.",
                        severity="error",
                        context="Transactions/Transaction",
                    )
                )
        return issues

    def _check_uetr(self, root: ET.Element, ns: dict) -> Iterable[ValidationIssue]:
        issues: List[ValidationIssue] = []
        uetr_pattern = re.compile(r"^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$")
        for node in root.findall(".//ns:UETR", ns):
            value = (node.text or "").strip()
            if not value:
                issues.append(
                    ValidationIssue(
                        code="missing_uetr",
                        message="Transaction UETR is empty.",
                        severity="error",
                        context="Transactions/Transaction/UETR",
                    )
                )
            elif value.lower() in PLACEHOLDER_VALUES:
                issues.append(
                    ValidationIssue(
                        code="placeholder_uetr",
                        message=f"Transaction UETR contains placeholder value '{value}'.",
                        severity="error",
                        context="Transactions/Transaction/UETR",
                    )
                )
            elif not uetr_pattern.match(value):
                issues.append(
                    ValidationIssue(
                        code="invalid_uetr_format",
                        message="Transaction UETR must follow the 8-4-4-4-12 GUID pattern.",
                        severity="warning",
                        context="Transactions/Transaction/UETR",
                    )
                )
        return issues

    def _find_text(self, element: ET.Element, path: str, ns: dict) -> Optional[str]:
        found = element.find(path, ns)
        if found is None or found.text is None:
            return None
        text = found.text.strip()
        return text or None

    def _parse_iso_date(self, value: str) -> Optional[date]:
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None

    def _is_positive_decimal(self, value: str) -> bool:
        try:
            return Decimal(value) > 0
        except (InvalidOperation, ValueError):
            return False

    def _namespace(self, root: ET.Element) -> dict:
        if root.tag.startswith("{") and "}" in root.tag:
            uri = root.tag[1 : root.tag.index("}")]
            return {"ns": uri}
        return {}


def validate_file(path: Path, *, today: Optional[date] = None) -> List[ValidationIssue]:
    """Convenience function to validate a SAR file."""
    return SarValidator(today=today).validate_file(path)
