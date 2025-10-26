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

        content, read_issues = self._read_xml(path)
        issues.extend(read_issues)
        if content is None:
            return self._dedupe_issues(issues)

        try:
            root = ET.fromstring(content)
        except ET.ParseError as exc:
            issues.append(
                ValidationIssue(
                    code="malformed_xml",
                    message=f"XML parsing failed: {exc}",
                    severity="error",
                )
            )
            return self._dedupe_issues(issues)

        ns = self._namespace(root)

        issues.extend(self._check_filing_information(root, ns))
        transactions_container = root.find(".//ns:Transactions", ns)
        transactions = root.findall(".//ns:Transaction", ns)

        issues.extend(self._check_transactions(transactions_container, transactions, ns))
        issues.extend(self._check_uetr(transactions, ns))
        issues.extend(self._check_duplicate_uetr(transactions, ns))

        return self._dedupe_issues(issues)

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

    def _check_transactions(
        self,
        transactions_container: Optional[ET.Element],
        transactions: List[ET.Element],
        ns: dict,
    ) -> Iterable[ValidationIssue]:
        issues: List[ValidationIssue] = []

        if transactions_container is None:
            issues.append(
                ValidationIssue(
                    code="missing_transactions_section",
                    message="Transactions element is missing from the filing.",
                    severity="error",
                    context="Transactions",
                )
            )
            return issues

        if not transactions:
            issues.append(
                ValidationIssue(
                    code="missing_transaction_entries",
                    message="Transactions element does not contain any Transaction entries.",
                    severity="error",
                    context="Transactions",
                )
            )
            return issues

        for index, txn in enumerate(transactions, start=1):
            txn_context = f"Transactions/Transaction[{index}]"
            date_text = self._find_text(txn, "ns:Date", ns)
            if date_text:
                parsed = self._parse_iso_date(date_text)
                if parsed is None:
                    issues.append(
                        ValidationIssue(
                            code="invalid_transaction_date",
                            message=f"Transaction date '{date_text}' is not a valid ISO-8601 date.",
                            severity="error",
                            context=f"{txn_context}/Date",
                        )
                    )
                elif parsed > self.today:
                    issues.append(
                        ValidationIssue(
                            code="future_transaction_date",
                            message=f"Transaction date {date_text} occurs in the future relative to today ({self.today.isoformat()}).",
                            severity="warning",
                            context=f"{txn_context}/Date",
                        )
                    )
            else:
                issues.append(
                    ValidationIssue(
                        code="missing_transaction_date",
                        message="Transaction is missing Date element or value.",
                        severity="error",
                        context=f"{txn_context}/Date",
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
                            context=f"{txn_context}/Amount",
                        )
                    )
                elif amount_text.lower() in PLACEHOLDER_VALUES:
                    issues.append(
                        ValidationIssue(
                            code="placeholder_amount",
                            message=f"Transaction amount contains placeholder value '{amount_text}'.",
                            severity="error",
                            context=f"{txn_context}/Amount",
                        )
                    )
                else:
                    if not self._is_positive_decimal(amount_text):
                        issues.append(
                            ValidationIssue(
                                code="invalid_amount",
                                message=f"Transaction amount '{amount_text}' is not a valid positive decimal.",
                                severity="error",
                                context=f"{txn_context}/Amount",
                            )
                        )
            else:
                issues.append(
                    ValidationIssue(
                        code="missing_amount_element",
                        message="Transaction is missing Amount element.",
                        severity="error",
                        context=txn_context,
                    )
                )
        return issues

    def _check_uetr(self, transactions: List[ET.Element], ns: dict) -> Iterable[ValidationIssue]:
        issues: List[ValidationIssue] = []
        uetr_pattern = re.compile(r"^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$")
        for index, txn in enumerate(transactions, start=1):
            context = f"Transactions/Transaction[{index}]/UETR"
            node = txn.find("ns:UETR", ns)
            if node is None:
                issues.append(
                    ValidationIssue(
                        code="missing_uetr_element",
                        message="Transaction is missing UETR element.",
                        severity="error",
                        context=context,
                    )
                )
                continue
            value = (node.text or "").strip()
            if not value:
                issues.append(
                    ValidationIssue(
                        code="missing_uetr",
                        message="Transaction UETR is empty.",
                        severity="error",
                        context=context,
                    )
                )
            elif value.lower() in PLACEHOLDER_VALUES:
                issues.append(
                    ValidationIssue(
                        code="placeholder_uetr",
                        message=f"Transaction UETR contains placeholder value '{value}'.",
                        severity="error",
                        context=context,
                    )
                )
            elif not uetr_pattern.match(value):
                issues.append(
                    ValidationIssue(
                        code="invalid_uetr_format",
                        message="Transaction UETR must follow the 8-4-4-4-12 GUID pattern.",
                        severity="warning",
                        context=context,
                    )
                )
        return issues

    def _check_duplicate_uetr(self, transactions: List[ET.Element], ns: dict) -> Iterable[ValidationIssue]:
        issues: List[ValidationIssue] = []
        seen: dict[str, int] = {}
        for index, txn in enumerate(transactions, start=1):
            value = self._find_text(txn, "ns:UETR", ns)
            if not value:
                continue
            normalized = value.lower()
            if normalized in PLACEHOLDER_VALUES:
                continue
            if normalized in seen:
                first_index = seen[normalized]
                issues.append(
                    ValidationIssue(
                        code="duplicate_uetr",
                        message=(
                            f"Transaction UETR '{value}' duplicates value from Transaction[{first_index}]."
                        ),
                        severity="error",
                        context=f"Transactions/Transaction[{index}]/UETR",
                    )
                )
            else:
                seen[normalized] = index
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

    def _read_xml(self, path: Path) -> tuple[Optional[str], List[ValidationIssue]]:
        issues: List[ValidationIssue] = []
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            issues.append(
                ValidationIssue(
                    code="read_error",
                    message=f"Unable to read file: {exc}",
                    severity="error",
                    context=str(path),
                )
            )
            return None, issues

        if not content.strip():
            issues.append(
                ValidationIssue(
                    code="empty_file",
                    message="SAR file is empty.",
                    severity="error",
                    context=str(path),
                )
            )
            return None, issues

        return content, issues

    def _dedupe_issues(self, issues: Iterable[ValidationIssue]) -> List[ValidationIssue]:
        deduped: List[ValidationIssue] = []
        seen = set()
        for issue in issues:
            key = (issue.code, issue.context, issue.message, issue.severity)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(issue)
        return deduped


def validate_file(path: Path, *, today: Optional[date] = None) -> List[ValidationIssue]:
    """Convenience function to validate a SAR file."""
    return SarValidator(today=today).validate_file(path)
