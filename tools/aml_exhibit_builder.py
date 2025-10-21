#!/usr/bin/env python3
"""Utility for building AML exhibit summaries.

This script creates a compact summary of packet, network, and capture
metadata so analysts can quickly embed it into AML filings or supporting
documentation.  The tool emits either Markdown (default) or JSON, and it can
optionally persist the output to disk.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import OrderedDict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional


@dataclass
class NetworkProfile:
    """Normalized representation of the radio access metadata."""

    imsi_prefix: str
    sim_country_iso: str
    network_operator: str
    network_operator_name: str
    network_type: str
    msisdn: str


@dataclass
class CaptureContext:
    """Encapsulates provenance information for the capture."""

    source: str
    references: List[str]


@dataclass
class TransactionRecord:
    """Flexible row of key/value pairs for transaction tables."""

    fields: "OrderedDict[str, str]"


@dataclass
class TelecomMetadata:
    """Structured representation of telecom registration details."""

    fields: "OrderedDict[str, str]"
    notes: List[str]


@dataclass
class Certification:
    """Holds certification statement and signature context."""

    statement: Optional[str]
    signatory: Optional[str]
    title: Optional[str]
    entity: Optional[str]
    bates_number: Optional[str]


@dataclass
class TextSection:
    """Represents additional free-form sections to append."""

    title: str
    content: str


@dataclass
class Attachment:
    """Represents attachment metadata to list within the exhibit."""

    filename: str
    description: Optional[str]


@dataclass
class ExhibitPacket:
    """Data model for the generated exhibit packet."""

    packet_id: str
    scheme: str
    network_profile: NetworkProfile
    capture_context: CaptureContext
    generated_at: str
    title: str
    subtitle: Optional[str]
    transactions_title: Optional[str]
    transactions: List[TransactionRecord]
    telecom_title: Optional[str]
    telecom_metadata: Optional[TelecomMetadata]
    certification: Optional[Certification]
    additional_sections: List[TextSection]
    attachments: List[Attachment]
    sar_xml: Optional[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a formatted AML exhibit for telephony metadata.",
    )
    parser.add_argument(
        "--title",
        default="AML Exhibit",
        help="Primary document title (default: 'AML Exhibit').",
    )
    parser.add_argument(
        "--subtitle",
        help="Optional subtitle to render beneath the title.",
    )
    parser.add_argument("--packet-id", required=True, help="Unique packet identifier.")
    parser.add_argument(
        "--imsi-prefix",
        required=True,
        help="The IMSI prefix associated with the capture (e.g., MCC+MNC).",
    )
    parser.add_argument(
        "--sim-country-iso",
        required=True,
        help="ISO 3166-1 alpha-2 code for the SIM country.",
    )
    parser.add_argument(
        "--network-operator",
        required=True,
        help="Numeric network operator code (MCC+MNC).",
    )
    parser.add_argument(
        "--network-operator-name",
        required=True,
        help="Human-readable name for the network operator.",
    )
    parser.add_argument(
        "--network-type",
        required=True,
        help="Type of radio network involved in the capture (e.g., LTE, NR).",
    )
    parser.add_argument("--msisdn", required=True, help="Subscriber MSISDN.")
    parser.add_argument(
        "--capture-source",
        required=True,
        help="Primary source from which the capture metadata was derived.",
    )
    parser.add_argument(
        "--capture-refs",
        nargs="+",
        default=[],
        help="Pointers to supporting evidence (log lines, hashes, etc.).",
    )
    parser.add_argument(
        "--scheme",
        required=True,
        help="Brief description of the fraud or laundering scheme.",
    )
    parser.add_argument(
        "--transactions-title",
        default="Transactions of Concern",
        help="Heading for the transactions section.",
    )
    parser.add_argument(
        "--transactions-csv",
        help="Path to a CSV file describing transaction rows.",
    )
    parser.add_argument(
        "--transaction",
        action="append",
        default=[],
        help=(
            "Transaction row provided as semicolon-separated key=value pairs "
            "(e.g., 'Date=2023-02-09; Amount (USD)=5000')."
        ),
    )
    parser.add_argument(
        "--telecom-title",
        default="Telecom Metadata",
        help="Heading for the telecom metadata section.",
    )
    parser.add_argument(
        "--telecom-json",
        help="Path to a JSON file containing telecom metadata key/value pairs.",
    )
    parser.add_argument(
        "--telecom-field",
        action="append",
        default=[],
        help="Telecom metadata field in KEY=VALUE form. Can be specified multiple times.",
    )
    parser.add_argument(
        "--telecom-note",
        action="append",
        default=[],
        help="Additional narrative text appended after the telecom metadata table.",
    )
    parser.add_argument(
        "--certification-text",
        help="Body of the certification statement.",
    )
    parser.add_argument(
        "--certification-signatory",
        help="Name of the individual signing the certification.",
    )
    parser.add_argument(
        "--certification-title",
        help="Title or role of the signatory.",
    )
    parser.add_argument(
        "--certification-entity",
        help="Affiliated entity for the certification signature block.",
    )
    parser.add_argument(
        "--certification-bates",
        help="Optional Bates number to append to the certification block.",
    )
    parser.add_argument(
        "--additional-section",
        action="append",
        default=[],
        help=(
            "Additional section in 'Title:Content' format. Content supports newline escape "
            "sequences (\\n) for multi-paragraph text."
        ),
    )
    parser.add_argument(
        "--attachment",
        action="append",
        default=[],
        help=(
            "Attachment entry described as 'filename|description'. Description is optional."
        ),
    )
    parser.add_argument(
        "--sar-xml",
        help=(
            "Inline SAR XML payload to embed directly. Use with caution for large files."
        ),
    )
    parser.add_argument(
        "--sar-xml-file",
        help=(
            "Path to a SAR XML payload to embed as a fenced code block. Use '-' to read from stdin."
        ),
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format (default: markdown).",
    )
    parser.add_argument(
        "--output",
        help="Optional path where the rendered exhibit should be written.",
    )
    return parser.parse_args()


def _normalize_capture_refs(raw_refs: Iterable[str]) -> List[str]:
    """Split capture references on separators while preserving inline spaces."""

    normalized: List[str] = []
    separators = re.compile(r"(?:\s*[;|]\s*|\s*\\n\s*)")
    for entry in raw_refs:
        if entry is None:
            continue
        stripped = entry.strip()
        if not stripped:
            continue
        fragments = [frag.strip() for frag in separators.split(stripped) if frag.strip()]
        if fragments:
            normalized.extend(fragments)
        else:
            normalized.append(stripped)
    return normalized


def _parse_semicolon_kv_pairs(entry: str) -> "OrderedDict[str, str]":
    """Parse KEY=VALUE pairs separated by semicolons, retaining insertion order."""

    ordered: "OrderedDict[str, str]" = OrderedDict()
    if not entry:
        return ordered
    # Split on semicolons that are not escaped.
    segments = [segment.strip() for segment in entry.split(";") if segment.strip()]
    for segment in segments:
        if "=" not in segment:
            raise ValueError(f"Missing '=' in transaction field definition: {segment}")
        key, value = segment.split("=", 1)
        ordered[key.strip()] = value.strip()
    return ordered


def _load_transactions(args: argparse.Namespace) -> List[TransactionRecord]:
    """Aggregate transaction rows from CSV files and CLI-supplied entries."""

    records: List[TransactionRecord] = []
    if args.transactions_csv:
        path = Path(args.transactions_csv)
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise ValueError("Transactions CSV must include a header row.")
            for row in reader:
                ordered = OrderedDict((field, row.get(field, "")) for field in reader.fieldnames)
                records.append(TransactionRecord(fields=ordered))
    for raw in args.transaction:
        ordered = _parse_semicolon_kv_pairs(raw)
        if ordered:
            records.append(TransactionRecord(fields=ordered))
    return records


def _load_telecom_metadata(args: argparse.Namespace) -> Optional[TelecomMetadata]:
    """Create telecom metadata mapping from JSON file and key=value inputs."""

    fields: "OrderedDict[str, str]" = OrderedDict()
    if args.telecom_json:
        data_path = Path(args.telecom_json)
        data = json.loads(data_path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for key, value in data.items():
                fields[str(key)] = "" if value is None else str(value)
        else:
            raise ValueError("Telecom JSON must be an object with key/value pairs.")
    for entry in args.telecom_field:
        if "=" not in entry:
            raise ValueError(f"Telecom field '{entry}' is missing '=' separator.")
        key, value = entry.split("=", 1)
        fields[key.strip()] = value.strip()
    if not fields and not args.telecom_note:
        return None
    return TelecomMetadata(fields=fields, notes=list(args.telecom_note))


def _parse_additional_sections(raw_sections: Iterable[str]) -> List[TextSection]:
    """Split Title:Content strings into structured text sections."""

    sections: List[TextSection] = []
    for entry in raw_sections:
        if ":" not in entry:
            raise ValueError(
                "Additional sections must be provided as 'Title:Content' pairs."
            )
        title, content = entry.split(":", 1)
        normalized_content = content.replace("\\n", "\n").strip()
        sections.append(TextSection(title=title.strip(), content=normalized_content))
    return sections


def _parse_attachments(raw_attachments: Iterable[str]) -> List[Attachment]:
    attachments: List[Attachment] = []
    for entry in raw_attachments:
        if "|" in entry:
            filename, description = entry.split("|", 1)
            attachments.append(
                Attachment(filename=filename.strip(), description=description.strip() or None)
            )
        else:
            attachments.append(Attachment(filename=entry.strip(), description=None))
    return attachments


def _load_sar_xml(
    inline_payload: Optional[str], path_str: Optional[str]
) -> Optional[str]:
    """Return SAR XML payload from inline text or the provided file path."""

    if inline_payload and path_str:
        raise ValueError("Specify either --sar-xml or --sar-xml-file, not both.")

    if inline_payload:
        return inline_payload

    if not path_str:
        return None

    if path_str == "-":
        # Read from stdin when the user explicitly opts in.
        return sys.stdin.read()

    path = Path(path_str)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"SAR XML file not found: {path_str}. Provide a valid path or use --sar-xml."
        ) from exc


def build_packet(args: argparse.Namespace) -> ExhibitPacket:
    network = NetworkProfile(
        imsi_prefix=args.imsi_prefix,
        sim_country_iso=args.sim_country_iso.upper(),
        network_operator=args.network_operator,
        network_operator_name=args.network_operator_name,
        network_type=args.network_type,
        msisdn=args.msisdn,
    )
    capture = CaptureContext(
        source=args.capture_source,
        references=_normalize_capture_refs(args.capture_refs),
    )
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    transactions = _load_transactions(args)
    telecom_metadata = _load_telecom_metadata(args)
    certification = Certification(
        statement=args.certification_text,
        signatory=args.certification_signatory,
        title=args.certification_title,
        entity=args.certification_entity,
        bates_number=args.certification_bates,
    )
    if not any(
        [
            certification.statement,
            certification.signatory,
            certification.title,
            certification.entity,
            certification.bates_number,
        ]
    ):
        certification_obj: Optional[Certification] = None
    else:
        certification_obj = certification
    return ExhibitPacket(
        packet_id=args.packet_id,
        scheme=args.scheme,
        network_profile=network,
        capture_context=capture,
        generated_at=generated_at,
        title=args.title,
        subtitle=args.subtitle,
        transactions_title=args.transactions_title if transactions else None,
        transactions=transactions,
        telecom_title=args.telecom_title if telecom_metadata else None,
        telecom_metadata=telecom_metadata,
        certification=certification_obj,
        additional_sections=_parse_additional_sections(args.additional_section),
        attachments=_parse_attachments(args.attachment),
        sar_xml=_load_sar_xml(args.sar_xml, args.sar_xml_file),
    )


def render_markdown(packet: ExhibitPacket) -> str:
    network_rows = [
        ("IMSI Prefix", packet.network_profile.imsi_prefix),
        ("SIM Country ISO", packet.network_profile.sim_country_iso),
        ("Network Operator", packet.network_profile.network_operator),
        ("Operator Name", packet.network_profile.network_operator_name),
        ("Network Type", packet.network_profile.network_type),
        ("MSISDN", packet.network_profile.msisdn),
    ]

    lines = [f"# {packet.title}"]
    if packet.subtitle:
        lines.extend(["", packet.subtitle.strip()])
    lines.append("")
    lines.append(f"**Packet ID:** {packet.packet_id}")
    lines.append(f"**Scheme:** {packet.scheme}")
    lines.append(f"**Generated At:** {packet.generated_at}")
    lines.append("")

    lines.append("## Network Profile")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    for label, value in network_rows:
        lines.append(f"| {label} | {value} |")
    lines.append("")

    lines.append("## Capture Context")
    lines.append(f"**Source:** {packet.capture_context.source}")
    if packet.capture_context.references:
        lines.append("**References:**")
        for ref in packet.capture_context.references:
            lines.append(f"- {ref}")
    else:
        lines.append("**References:** _None provided_")

    if packet.transactions:
        lines.append("")
        lines.append(f"## {packet.transactions_title}")
        # Determine the union of all column headers while preserving insertion order.
        headers: List[str] = []
        for record in packet.transactions:
            for key in record.fields.keys():
                if key not in headers:
                    headers.append(key)
        if headers:
            header_row = " | ".join(headers)
            lines.append(f"| {header_row} |")
            lines.append(f"| {' | '.join(['---'] * len(headers))} |")
            for record in packet.transactions:
                row = [record.fields.get(header, "") for header in headers]
                lines.append(f"| {' | '.join(row)} |")

    if packet.telecom_metadata and packet.telecom_metadata.fields:
        lines.append("")
        lines.append(f"## {packet.telecom_title}")
        lines.append("| Field | Value |")
        lines.append("| --- | --- |")
        for key, value in packet.telecom_metadata.fields.items():
            lines.append(f"| {key} | {value} |")
        if packet.telecom_metadata.notes:
            lines.append("")
            for note in packet.telecom_metadata.notes:
                lines.append(note)

    if packet.certification:
        lines.append("")
        lines.append("## Certification")
        if packet.certification.statement:
            lines.append(packet.certification.statement)
        signature_lines: List[str] = []
        if packet.certification.signatory:
            signature_lines.append(f"/s/ {packet.certification.signatory}")
        if packet.certification.title:
            signature_lines.append(packet.certification.title)
        if packet.certification.entity:
            signature_lines.append(packet.certification.entity)
        if signature_lines:
            lines.append("")
            lines.extend(signature_lines)
        if packet.certification.bates_number:
            lines.append("")
            lines.append(f"BATES No. {packet.certification.bates_number}")

    for section in packet.additional_sections:
        lines.append("")
        lines.append(f"## {section.title}")
        lines.append(section.content)

    if packet.attachments:
        lines.append("")
        lines.append("## Attachments")
        for attachment in packet.attachments:
            if attachment.description:
                lines.append(f"- **{attachment.filename}** – {attachment.description}")
            else:
                lines.append(f"- **{attachment.filename}**")

    if packet.sar_xml:
        lines.append("")
        lines.append("## SAR XML Payload")
        lines.append("```xml")
        lines.append(packet.sar_xml.strip())
        lines.append("```")

    return "\n".join(lines)


def render_json(packet: ExhibitPacket) -> str:
    # Convert dataclass hierarchy into serializable form.
    payload = asdict(packet)
    return json.dumps(payload, indent=2, ensure_ascii=False)


def write_output(text: str, output_path: str | None) -> None:
    if not output_path:
        return
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    packet = build_packet(args)
    if args.format == "markdown":
        rendered = render_markdown(packet)
    else:
        rendered = render_json(packet)
    write_output(rendered, args.output)
    print(rendered)


if __name__ == "__main__":
    main()
