"""Summaries for the Stop AZS escrow diversion dataset."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

DATA_PATH = Path(__file__).parent / "data" / "network.json"


@dataclass
class Transaction:
    """Representation of a recorded or pending transaction."""

    tx_id: str
    amount: Optional[float]
    currency: Optional[str]
    origin: str
    destination: Optional[str] = None
    datetime: Optional[str] = None
    date: Optional[str] = None
    obi: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    beneficiaries: Optional[Sequence[str]] = None
    pass_through_accounts: Optional[Sequence[str]] = None
    uet_r: Optional[str] = None

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "Transaction":
        raw_amount = payload.get("amount")
        amount: Optional[float]
        if isinstance(raw_amount, (int, float)):
            amount = float(raw_amount)
        elif isinstance(raw_amount, str):
            cleaned = raw_amount.replace("$", "").replace(",", "").strip()
            try:
                amount = float(cleaned)
            except ValueError:
                amount = None
        else:
            amount = None

        uetr_value = payload.get("uet_r")
        if uetr_value is None:
            uetr_value = payload.get("uetr")
        if uetr_value is None:
            uetr_value = payload.get("UETR")

        return cls(
            tx_id=str(payload.get("id", "unknown")),
            amount=amount,
            currency=str(payload.get("currency")) if payload.get("currency") is not None else None,
            origin=str(payload.get("origin", "Unknown origin")),
            destination=str(payload.get("destination")) if payload.get("destination") is not None else None,
            datetime=str(payload.get("datetime")) if payload.get("datetime") is not None else None,
            date=str(payload.get("date")) if payload.get("date") is not None else None,
            obi=str(payload.get("obi")) if payload.get("obi") is not None else None,
            notes=str(payload.get("notes")) if payload.get("notes") is not None else None,
            status=str(payload.get("status")) if payload.get("status") is not None else None,
            beneficiaries=tuple(str(item) for item in payload.get("beneficiaries", []) if item is not None),
            pass_through_accounts=tuple(
                str(item)
                for item in payload.get("pass_through_accounts", [])
                if item is not None
            ),
            uet_r=str(uetr_value) if uetr_value is not None else None,
        )


def load_data(path: Path = DATA_PATH) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_transactions(raw: Mapping[str, Any], key: str) -> List[Transaction]:
    entries = raw.get(key, [])
    return [Transaction.from_dict(item) for item in entries if isinstance(item, Mapping)]


def total_amount(transactions: Iterable[Transaction]) -> float:
    return sum(tx.amount for tx in transactions if tx.amount is not None)


def format_amount(amount: Optional[float], currency: Optional[str]) -> str:
    if amount is None:
        return "Amount pending"
    symbol = "$" if currency == "USD" else ""
    formatted = f"{amount:,.2f}" if amount is not None else "Unknown"
    return f"{symbol}{formatted}" if symbol else formatted


def format_transaction(tx: Transaction) -> str:
    pieces: List[str] = [f"ID {tx.tx_id}"]
    if tx.datetime:
        pieces.append(f"timestamp {tx.datetime}")
    elif tx.date:
        pieces.append(f"date {tx.date}")

    pieces.append(format_amount(tx.amount, tx.currency))
    pieces.append(f"origin: {tx.origin}")
    if tx.destination:
        pieces.append(f"destination: {tx.destination}")
    if tx.obi:
        pieces.append(f"OBI '{tx.obi}'")
    if tx.pass_through_accounts:
        accounts = ", ".join(tx.pass_through_accounts)
        pieces.append(f"pass-through accounts: {accounts}")
    if tx.beneficiaries:
        beneficiaries = ", ".join(tx.beneficiaries)
        pieces.append(f"beneficiaries: {beneficiaries}")
    if tx.uet_r:
        pieces.append(f"UETR: {tx.uet_r}")
    if tx.status:
        pieces.append(f"status: {tx.status}")
    if tx.notes:
        pieces.append(f"notes: {tx.notes}")
    return "; ".join(pieces)


def describe_account_gaps(account_info: Mapping[str, Any]) -> Tuple[str, Optional[str]]:
    """Return account description and any gap note."""

    account_number = account_info.get("number") or account_info.get("account_number")
    financial_institution = account_info.get("financial_institution")
    bits: List[str] = []
    if account_number:
        bits.append(f"account {account_number}")
    if financial_institution:
        bits.append(f"institution {financial_institution}")
    descriptor = ", ".join(bits)
    if descriptor:
        gap_note: Optional[str] = None
    else:
        gap_note = "account details pending subpoena"
    return descriptor, gap_note


def collect_pending_items(
    data: Mapping[str, Any],
    recorded: Sequence[Transaction],
    pending: Sequence[Transaction],
    sar_transactions: Sequence[Transaction],
    documented_categories: Optional[Set[str]] = None,
) -> List[str]:
    """Identify outstanding information gaps for follow-up."""

    pending_items: List[str] = []

    def record_gap(message: str, category: Optional[str] = None) -> None:
        if (
            documented_categories
            and category
            and category in documented_categories
        ):
            message = f"{message} (documented in information sink)"
        pending_items.append(message)

    sar_filing = data.get("sar_filing", {})
    if isinstance(sar_filing, Mapping):
        filer_information = sar_filing.get("filer_information", {})
        if isinstance(filer_information, Mapping):
            ein = filer_information.get("ein")
            if not ein:
                record_gap(
                    "Filer EIN confirmation outstanding (blank in SAR metadata).",
                    category="Filer EIN",
                )

        subjects = sar_filing.get("subjects", [])
        if isinstance(subjects, Sequence) and not isinstance(subjects, (str, bytes)):
            for subject in subjects:
                if not isinstance(subject, Mapping):
                    continue
                name = subject.get("name") or "Unnamed subject"
                account_info = subject.get("account")
                if isinstance(account_info, Mapping):
                    _, gap_note = describe_account_gaps(account_info)
                    if gap_note:
                        record_gap(
                            f"Account identifiers for {name} are {gap_note}.",
                            category="Beneficiary account identifiers",
                        )

    def note_transaction(tx: Transaction, source: str) -> None:
        if tx.amount is None:
            record_gap(
                f"Amount for {source} transaction '{tx.tx_id}' remains pending subpoena."
            )
        if not tx.uet_r or tx.uet_r.upper() == "PENDING":
            record_gap(
                f"UETR for {source} transaction '{tx.tx_id}' still awaiting bank response.",
                category="UETR identifiers",
            )

    for tx in pending:
        note_transaction(tx, "escrow trail")

    for tx in sar_transactions:
        note_transaction(tx, "SAR follow-up")

    for tx in recorded:
        if tx.currency is None:
            record_gap(
                f"Currency designation missing for recorded transaction '{tx.tx_id}'."
            )

    entities = data.get("entities", {})
    if isinstance(entities, Mapping):
        for category, entries in entities.items():
            if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes)):
                continue
            for entry in entries:
                if not isinstance(entry, Mapping):
                    continue
                name = entry.get("name") or "Unnamed entity"
                role = entry.get("role")
                jurisdiction = entry.get("jurisdiction")
                if not role:
                    record_gap(
                        f"Role details outstanding for {name} in entity category '{category}'."
                    )
                if not jurisdiction:
                    record_gap(
                        f"Jurisdiction confirmation pending for {name} in entity category '{category}'."
                    )

    properties = data.get("properties", [])
    if isinstance(properties, Sequence) and not isinstance(properties, (str, bytes)):
        for property_entry in properties:
            if not isinstance(property_entry, Mapping):
                continue
            address = property_entry.get("address") or "Unnamed property"
            status = property_entry.get("status")
            if isinstance(status, str) and "unverified" in status.lower():
                record_gap(
                    f"Property '{address}' flagged '{status}' awaiting corroboration.",
                    category="Control verification",
                )

    attachments = data.get("attachments", [])
    if isinstance(attachments, Sequence) and not isinstance(attachments, (str, bytes)):
        for attachment in attachments:
            if not isinstance(attachment, Mapping):
                continue
            description = attachment.get("description")
            if description:
                continue
            attachment_id = attachment.get("id") or attachment.get("file") or "Unnamed attachment"
            record_gap(
                f"Attachment '{attachment_id}' needs a descriptive summary for investigative indexing."
            )

    contacts = data.get("law_enforcement_contacts", [])
    if isinstance(contacts, Sequence) and not isinstance(contacts, (str, bytes)):
        for contact in contacts:
            if not isinstance(contact, Mapping):
                continue
            agency = contact.get("agency") or "Unknown agency"
            reference = contact.get("reference")
            requested_action = contact.get("requested_action")
            if not reference:
                record_gap(
                    f"Reference identifier pending for law-enforcement contact '{agency}'."
                )
            if not requested_action:
                record_gap(
                    f"Requested action detail outstanding for law-enforcement contact '{agency}'."
                )

    return sorted(set(pending_items))


def summarise() -> str:
    data = load_data()
    trail: Mapping[str, Any] = data.get("transaction_trail", {})
    recorded = load_transactions(trail, "transactions")
    pending = load_transactions(trail, "pending_transactions")

    lines = [
        "Stop AZS Escrow Diversion Snapshot",
        "==================================",
    ]

    submission = data.get("submission", {})
    if submission:
        tracking_id = submission.get("ic3_tracking_id")
        if tracking_id:
            lines.append(f"IC3 tracking ID: {tracking_id}")
        report_date = submission.get("report_date")
        if report_date:
            lines.append(f"Report date: {report_date}")
        timezone = submission.get("timezone")
        if timezone:
            lines.append(f"Timezone: {timezone}")
        narrative = submission.get("narrative_summary")
        if narrative:
            lines.extend(["", "Narrative summary:", f"  {narrative}"])

    property_name = trail.get("property")
    if property_name:
        lines.extend(["", f"Primary property: {property_name}"])

    escrow_account = trail.get("escrow_account")
    if isinstance(escrow_account, Mapping):
        bank = escrow_account.get("bank")
        account_number = escrow_account.get("account_number")
        holder = escrow_account.get("holder")
        details: List[str] = []
        if bank:
            details.append(bank)
        if account_number:
            details.append(f"account {account_number}")
        if holder:
            details.append(f"holder {holder}")
        if details:
            lines.append("  Escrow account: " + ", ".join(details))

    sar_filing = data.get("sar_filing")
    sar_transactions: List[Transaction] = []
    if isinstance(sar_filing, Mapping):
        filing_information = sar_filing.get("filing_information", {})
        if isinstance(filing_information, Mapping):
            lines.append("")
            lines.append("FinCEN filing information:")
            filing_fields = {
                "Filing type": filing_information.get("filing_type"),
                "Filing date": filing_information.get("filing_date"),
                "Amendment type": filing_information.get("amendment_type"),
                "Contact office": filing_information.get("contact_office"),
                "Contact phone": filing_information.get("contact_phone"),
                "Contact email": filing_information.get("contact_email"),
            }
            for label, value in filing_fields.items():
                if value:
                    lines.append(f"  {label}: {value}")

        filer_information = sar_filing.get("filer_information", {})
        if isinstance(filer_information, Mapping):
            name = filer_information.get("name")
            address = filer_information.get("address")
            sam = filer_information.get("sam")
            ein_value = filer_information.get("ein")
            if name or address or sam or ein_value is not None:
                lines.append("")
                lines.append("Filer details:")
                if name:
                    lines.append(f"  Name: {name}")
                if isinstance(address, Mapping):
                    address_bits = [
                        address.get("line1"),
                        address.get("city"),
                        address.get("state"),
                        address.get("zip"),
                        address.get("country"),
                    ]
                    formatted_address = ", ".join(
                        str(bit) for bit in address_bits if bit
                    )
                    if formatted_address:
                        lines.append(f"  Address: {formatted_address}")
                if isinstance(sam, Mapping):
                    uei = sam.get("uei")
                    cage = sam.get("cage")
                    if uei or cage:
                        details: List[str] = []
                        if uei:
                            details.append(f"UEI {uei}")
                        if cage:
                            details.append(f"CAGE {cage}")
                        lines.append(f"  SAM registrations: {', '.join(details)}")
                if ein_value:
                    lines.append(f"  EIN: {ein_value}")
                elif ein_value == "":
                    lines.append("  EIN: not provided")
                elif ein_value is None:
                    lines.append("  EIN: pending confirmation")

        subjects = sar_filing.get("subjects", [])
        if isinstance(subjects, Sequence) and not isinstance(subjects, (str, bytes)):
            subject_lines: List[str] = []
            for subject in subjects:
                if not isinstance(subject, Mapping):
                    continue
                name = subject.get("name")
                if not name:
                    continue
                descriptor: List[str] = [str(name)]
                entity_type = subject.get("entity_type")
                if entity_type:
                    descriptor.append(f"type: {entity_type}")
                account_info = subject.get("account")
                if isinstance(account_info, Mapping):
                    account_descriptor, gap_note = describe_account_gaps(account_info)
                    if account_descriptor:
                        descriptor.append(account_descriptor)
                    if gap_note:
                        descriptor.append(gap_note)
                subject_lines.append("    - " + "; ".join(descriptor))
            if subject_lines:
                lines.append("")
                lines.append("Subjects of SAR focus:")
                lines.extend(subject_lines)

        sar_transactions = load_transactions(sar_filing, "transactions")
        if sar_transactions:
            lines.append("")
            lines.append("SAR-documented follow-up transactions:")
            for tx in sar_transactions:
                lines.append(f"  - {format_transaction(tx)}")

        sar_attachments = sar_filing.get("attachments", [])
        if sar_attachments:
            lines.append("")
            lines.append("SAR attachments:")
            for attachment in sar_attachments:
                if not isinstance(attachment, Mapping):
                    continue
                file_name = attachment.get("file") or attachment.get("file_name")
                description = attachment.get("description")
                descriptor = "  - " + (str(file_name) if file_name else "Unnamed attachment")
                if description:
                    descriptor += f" – {description}"
                lines.append(descriptor)

        suspicious_activity = sar_filing.get("suspicious_activity", {})
        if isinstance(suspicious_activity, Mapping):
            activities = suspicious_activity.get("activities", [])
            if activities:
                lines.append("")
                lines.append("Suspicious activity categories:")
                for activity in activities:
                    lines.append(f"  - {activity}")
            locations = suspicious_activity.get("locations", [])
            if locations:
                lines.append("")
                lines.append("Locations of interest:")
                for location in locations:
                    lines.append(f"  - {location}")
            narrative = suspicious_activity.get("narrative")
            if narrative:
                lines.extend(["", "SAR narrative note:", f"  {narrative}"])

    lines.append("")
    total_recorded = total_amount(recorded)
    lines.append(f"Recorded suspicious amount: ${total_recorded:,.2f}" if total_recorded else "Recorded suspicious amount: Amount pending")

    if recorded:
        lines.extend(["", "Recorded transactions:"])
        for tx in recorded:
            lines.append(f"  - {format_transaction(tx)}")

    if pending:
        lines.extend(["", "Pending or subpoena-dependent transactions:"])
        for tx in pending:
            lines.append(f"  - {format_transaction(tx)}")

    information_sink = data.get("information_sink")
    documented_categories: Optional[Set[str]] = None
    if isinstance(information_sink, Mapping):
        missing_items = information_sink.get("missing", [])
        if isinstance(missing_items, Sequence) and not isinstance(missing_items, (str, bytes)):
            categories: Set[str] = set()
            for item in missing_items:
                if isinstance(item, Mapping):
                    category = item.get("category")
                    if isinstance(category, str) and category:
                        categories.add(category)
            if categories:
                documented_categories = categories

    pending_items = collect_pending_items(
        data,
        recorded,
        pending,
        sar_transactions,
        documented_categories=documented_categories,
    )
    if pending_items:
        lines.append("")
        lines.append("Outstanding information items:")
        for item in pending_items:
            lines.append(f"  - {item}")

    if isinstance(information_sink, Mapping):
        verified_items = information_sink.get("verified", [])
        missing_items = information_sink.get("missing", [])

        if isinstance(verified_items, Sequence) and not isinstance(verified_items, (str, bytes)):
            verified_lines: List[str] = []
            for item in verified_items:
                if not isinstance(item, Mapping):
                    continue
                category = item.get("category") or "Verified detail"
                details = item.get("details")
                sources = item.get("sources")
                line = f"  - {category}"
                if details:
                    line += f": {details}"
                verified_lines.append(line)
                if isinstance(sources, Sequence) and not isinstance(sources, (str, bytes)):
                    formatted_sources = ", ".join(str(source) for source in sources if source)
                    if formatted_sources:
                        verified_lines.append(f"      Sources: {formatted_sources}")
            if verified_lines:
                lines.append("")
                lines.append("Verified information checkpoints:")
                lines.extend(verified_lines)

        if isinstance(missing_items, Sequence) and not isinstance(missing_items, (str, bytes)):
            missing_lines: List[str] = []
            for item in missing_items:
                if not isinstance(item, Mapping):
                    continue
                category = item.get("category") or "Missing detail"
                details = item.get("details")
                dependency = item.get("dependency")
                line = f"  - {category}"
                if details:
                    line += f": {details}"
                missing_lines.append(line)
                if dependency:
                    missing_lines.append(f"      Dependency: {dependency}")
            if missing_lines:
                lines.append("")
                lines.append("Documented information gaps:")
                lines.extend(missing_lines)

    entities = data.get("entities", {})
    if entities:
        lines.append("")
        lines.append("Entities referenced:")
        for category, entries in entities.items():
            if not isinstance(entries, Sequence):
                continue
            lines.append(f"  {category}:")
            for entry in entries:
                if not isinstance(entry, Mapping):
                    continue
                descriptor: List[str] = [str(entry.get("name", "Unnamed entity"))]
                role = entry.get("role")
                if role:
                    descriptor.append(f"role: {role}")
                jurisdiction = entry.get("jurisdiction")
                if jurisdiction:
                    descriptor.append(f"jurisdiction: {jurisdiction}")
                lines.append("    - " + "; ".join(descriptor))

    properties = data.get("properties", [])
    if properties:
        lines.append("")
        lines.append("Properties of interest:")
        for property_entry in properties:
            if not isinstance(property_entry, Mapping):
                continue
            descriptor = [str(property_entry.get("address", "Unknown address"))]
            status = property_entry.get("status")
            if status:
                descriptor.append(f"status: {status}")
            notes = property_entry.get("notes")
            if notes:
                descriptor.append(f"notes: {notes}")
            lines.append("  - " + "; ".join(descriptor))

    indicators = data.get("indicators", [])
    if indicators:
        lines.append("")
        lines.append("Indicators observed:")
        for indicator in indicators:
            lines.append(f"  - {indicator}")

    affidavit = data.get("affidavit", {})
    if isinstance(affidavit, Mapping) and affidavit:
        lines.append("")
        title = affidavit.get("document_title") or "Affidavit"
        lines.append(f"{title}:")
        representative = affidavit.get("representative", {})
        if isinstance(representative, Mapping):
            rep_bits: List[str] = []
            rep_name = representative.get("name")
            if rep_name:
                rep_bits.append(rep_name)
            rep_title = representative.get("title")
            if rep_title:
                rep_bits.append(rep_title)
            organization = representative.get("organization")
            if organization:
                rep_bits.append(organization)
            identifiers: List[str] = []
            uei = representative.get("uei")
            cage = representative.get("cage")
            if uei:
                identifiers.append(f"UEI {uei}")
            if cage:
                identifiers.append(f"CAGE {cage}")
            if rep_bits:
                lines.append("  Representative: " + ", ".join(rep_bits))
            if identifiers:
                lines.append("  Identifiers: " + ", ".join(identifiers))
        authority_scope = affidavit.get("authority_scope", [])
        if authority_scope:
            lines.append("  Authority scope:")
            for item in authority_scope:
                lines.append(f"    - {item}")
        capabilities = affidavit.get("capabilities", [])
        if capabilities:
            lines.append("  Operational capabilities:")
            for item in capabilities:
                lines.append(f"    - {item}")
        statutes = affidavit.get("statutes", [])
        if statutes:
            lines.append("  Governing statutes and policies:")
            for item in statutes:
                lines.append(f"    - {item}")
        effective_period = affidavit.get("effective_period", {})
        if isinstance(effective_period, Mapping):
            start = effective_period.get("start")
            end = effective_period.get("end")
            if start or end:
                period_text = " to ".join(bit for bit in (start, end) if bit)
                lines.append(f"  Effective period: {period_text}")

    contacts = data.get("law_enforcement_contacts", [])
    if contacts:
        lines.append("")
        lines.append("Law enforcement contacts:")
        for contact in contacts:
            if not isinstance(contact, Mapping):
                continue
            agency = contact.get("agency", "Unknown agency")
            program = contact.get("program")
            line = f"  - {agency}"
            if program:
                line += f" ({program})"
            reference = contact.get("reference")
            if reference:
                line += f" – {reference}"
            lines.append(line)
            requested = contact.get("requested_action")
            if requested:
                lines.append(f"      Requested action: {requested}")

    attachments = data.get("attachments", [])
    if attachments:
        lines.append("")
        lines.append("Supporting attachments:")
        for item in attachments:
            if not isinstance(item, Mapping):
                continue
            descriptor = f"  - {item.get('id', 'Unknown id')}: {item.get('file', 'Unknown file')}"
            description = item.get("description")
            if description:
                descriptor += f" – {description}"
            lines.append(descriptor)

    return "\n".join(lines)


def main() -> None:
    print(summarise())


if __name__ == "__main__":
    main()
