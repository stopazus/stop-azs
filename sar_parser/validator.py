"""Validation helpers and CLI tooling for SAR XML payloads."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union
from xml.etree import ElementTree as ET

__all__ = [
    "validate_directory",
    "export_validation_report",
    "build_parser",
    "main",
]


NS = {"sar": "http://www.fincen.gov/base"}


def _path(value: Union[str, Path]) -> Path:
    if isinstance(value, Path):
        return value.expanduser()
    return Path(value).expanduser()


def _text(element: Optional[ET.Element]) -> Optional[str]:
    if element is None or element.text is None:
        return None
    value = element.text.strip()
    return value or None


def _gather_list(parent: Optional[ET.Element], tag: str) -> List[str]:
    if parent is None:
        return []
    return [value for value in (_text(child) for child in parent.findall(tag, NS)) if value]


def _parse_filing(root: ET.Element, errors: List[str]) -> Dict[str, Optional[str]]:
    filing = root.find("sar:FilingInformation", NS)
    if filing is None:
        errors.append("Missing FilingInformation section")
        return {}

    return {
        "filing_type": _text(filing.find("sar:FilingType", NS)),
        "filing_date": _text(filing.find("sar:FilingDate", NS)),
        "amendment_type": _text(filing.find("sar:AmendmentType", NS)),
        "contact_office": _text(filing.find("sar:ContactOffice", NS)),
        "contact_phone": _text(filing.find("sar:ContactPhone", NS)),
        "contact_email": _text(filing.find("sar:ContactEmail", NS)),
    }


def _parse_address(node: Optional[ET.Element]) -> Dict[str, Optional[str]]:
    if node is None:
        return {}
    return {
        "line1": _text(node.find("sar:AddressLine1", NS)),
        "line2": _text(node.find("sar:AddressLine2", NS)),
        "city": _text(node.find("sar:City", NS)),
        "state": _text(node.find("sar:State", NS)),
        "postal_code": _text(node.find("sar:ZIP", NS)),
        "country": _text(node.find("sar:Country", NS)),
    }


def _parse_filer(root: ET.Element, errors: List[str]) -> Dict[str, Any]:
    filer = root.find("sar:FilerInformation", NS)
    if filer is None:
        errors.append("Missing FilerInformation section")
        return {}

    sam = filer.find("sar:SAM", NS)
    return {
        "name": _text(filer.find("sar:FilerName", NS)),
        "ein": _text(filer.find("sar:FilerEIN", NS)),
        "address": _parse_address(filer.find("sar:FilerAddress", NS)),
        "sam": {
            "uei": _text(sam.find("sar:UEI", NS)) if sam is not None else None,
            "cage": _text(sam.find("sar:CAGE", NS)) if sam is not None else None,
        },
    }


def _parse_subjects(root: ET.Element) -> List[Dict[str, Optional[str]]]:
    subjects_node = root.find("sar:Subjects", NS)
    if subjects_node is None:
        return []

    subjects: List[Dict[str, Optional[str]]] = []
    for subject in subjects_node.findall("sar:Subject", NS):
        account = subject.find("sar:Account", NS)
        subjects.append(
            {
                "entity_type": _text(subject.find("sar:EntityType", NS)),
                "name": _text(subject.find("sar:Name", NS)),
                "account_number": _text(account.find("sar:AccountNumber", NS)) if account is not None else None,
                "financial_institution": _text(account.find("sar:FinancialInstitution", NS)) if account is not None else None,
            }
        )
    return subjects


def _parse_transactions(root: ET.Element) -> List[Dict[str, Any]]:
    transactions_node = root.find("sar:Transactions", NS)
    if transactions_node is None:
        return []

    transactions: List[Dict[str, Any]] = []
    for transaction in transactions_node.findall("sar:Transaction", NS):
        amount = transaction.find("sar:Amount", NS)
        pass_through = transaction.find("sar:PassThroughAccounts", NS)
        beneficiaries = transaction.find("sar:Beneficiaries", NS)
        transactions.append(
            {
                "date": _text(transaction.find("sar:Date", NS)),
                "amount": {
                    "currency": amount.attrib.get("currency") if amount is not None else None,
                    "value": _text(amount),
                },
                "originating_account": _text(transaction.find("sar:OriginatingAccount/sar:Name", NS)),
                "pass_through_accounts": _gather_list(pass_through, "sar:Account"),
                "beneficiaries": _gather_list(beneficiaries, "sar:Beneficiary"),
                "uetr": _text(transaction.find("sar:UETR", NS)),
                "notes": _text(transaction.find("sar:Notes", NS)),
            }
        )
    return transactions


def _parse_activity(root: ET.Element) -> Dict[str, Any]:
    activity = root.find("sar:SuspiciousActivity", NS)
    if activity is None:
        return {}

    return {
        "activities": _gather_list(activity.find("sar:Activities", NS), "sar:Activity"),
        "locations": _gather_list(activity.find("sar:Locations", NS), "sar:KnownAddress"),
        "narrative": _text(activity.find("sar:Narrative", NS)),
    }


def _parse_attachments(root: ET.Element) -> List[Dict[str, Optional[str]]]:
    attachments_node = root.find("sar:Attachments", NS)
    if attachments_node is None:
        return []

    attachments: List[Dict[str, Optional[str]]] = []
    for attachment in attachments_node.findall("sar:Attachment", NS):
        attachments.append(
            {
                "file_name": _text(attachment.find("sar:FileName", NS)),
                "description": _text(attachment.find("sar:Description", NS)),
            }
        )
    return attachments


def parse_sar(path: Path) -> Dict[str, Any]:
    tree = ET.parse(path)
    root = tree.getroot()
    local_name = root.tag.split("}")[-1]
    if local_name != "SAR":
        raise ValueError(f"Unexpected root element '{local_name}' in {path}")

    errors: List[str] = []
    filing = _parse_filing(root, errors)
    filer = _parse_filer(root, errors)

    if not filing.get("filing_type"):
        errors.append("Missing FilingType value")
    if not filer.get("name"):
        errors.append("Missing FilerName value")

    data: Dict[str, Any] = {
        "file": path.name,
        "version": root.attrib.get("version"),
        "filing": filing,
        "filer": filer,
        "subjects": _parse_subjects(root),
        "transactions": _parse_transactions(root),
        "suspicious_activity": _parse_activity(root),
        "attachments": _parse_attachments(root),
    }

    status = "ok" if not errors else "failed"
    data["validation"] = {"status": status, "errors": errors}
    return data


def validate_directory(directory: Path) -> Dict[str, Any]:
    directory = _path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"Validation directory not found: {directory}")
    if not directory.is_dir():
        raise ValueError(f"Validation path must be a directory, got: {directory}")

    xml_files = sorted(path for path in directory.glob("*.xml"))
    if not xml_files:
        raise FileNotFoundError(f"No SAR XML files found in {directory}")

    reports = [parse_sar(path) for path in xml_files]
    status = "ok" if all(report["validation"]["status"] == "ok" for report in reports) else "failed"

    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_directory": str(directory),
        "status": status,
        "reports": reports,
    }


def export_validation_report(report: Dict[str, Any], destination: Path) -> Path:
    destination = _path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, sort_keys=True))
    return destination


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sar-parser-validator",
        description="Validate SAR XML files and export evidentiary reports.",
    )
    parser.add_argument("--validate-dir", type=_path, required=True, help="Directory containing SAR XML files")
    parser.add_argument(
        "--export-report",
        type=_path,
        required=True,
        help="Destination path for the evidentiary JSON report",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    report = validate_directory(args.validate_dir)
    export_validation_report(report, args.export_report)

    total = len(report["reports"])
    status = report["status"]
    print(f"[INFO] Validated {total} SAR file(s) from {args.validate_dir} with status: {status}")
    print(f"[INFO] Validation report written to: {args.export_report}")
    return 0 if status == "ok" else 1


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
