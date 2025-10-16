#!/usr/bin/env python3
"""Utility for building AML exhibit summaries.

This script creates a compact summary of packet, network, and capture
metadata so analysts can quickly embed it into AML filings or supporting
documentation.  The tool emits either Markdown (default) or JSON, and it can
optionally persist the output to disk.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List
import re


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
class ExhibitPacket:
    """Data model for the generated exhibit packet."""

    packet_id: str
    scheme: str
    network_profile: NetworkProfile
    capture_context: CaptureContext
    generated_at: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a formatted AML exhibit for telephony metadata.",
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
    return ExhibitPacket(
        packet_id=args.packet_id,
        scheme=args.scheme,
        network_profile=network,
        capture_context=capture,
        generated_at=generated_at,
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

    lines = ["# AML Exhibit", ""]
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
