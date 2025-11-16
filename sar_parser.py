"""Utilities for parsing FinCEN Suspicious Activity Report (SAR) XML files.

The parser focuses on a handful of fields that investigators typically need at
first glance: high level filing metadata, declared subjects, and the set of
transactions documented in the report.  The goal is not to provide a complete
schema implementation, but instead to offer a lightweight way to surface the
most critical data points for triage or QA tooling.

The module exposes a :func:`parse_sar` helper that accepts XML content and
returns a :class:`SARData` dataclass containing normalized Python structures.
A small command line interface is also provided so the script can be executed
against a file path and emit JSON describing the parsed content.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Optional, Tuple, Type
import json
import sys
import xml.etree.ElementTree as ET

try:  # pragma: no cover - optional dependency path
    from defusedxml import ElementTree as _DefusedET
    from defusedxml.common import DefusedXmlException as _DefusedXmlException
except ImportError:  # pragma: no cover - exercised in unit tests
    _DefusedET = None
    _DEFUSED_SECURITY_ERRORS: Tuple[Type[BaseException], ...] = ()
else:  # pragma: no cover - exercised in unit tests
    _DEFUSED_SECURITY_ERRORS = (_DefusedXmlException,)

# The FinCEN SAR files use the base namespace as the default namespace.  We map
# it to the short prefix "f" so XPath expressions stay readable.
_NAMESPACE = {"f": "http://www.fincen.gov/base"}

_SECURITY_ERROR_MESSAGE = "SAR XML parsing blocked by security policy"


def _text_or_none(element: Optional[ET.Element]) -> Optional[str]:
    """Return the text content of ``element`` if present.

    Whitespace is stripped; empty strings are converted to ``None`` to avoid
    leaking placeholder values to downstream consumers.
    """

    if element is None:
        return None
    text = (element.text or "").strip()
    return text or None


@dataclass
class Subject:
    """Representation of an entity included in the SAR subjects section."""

    name: Optional[str]
    entity_type: Optional[str]


@dataclass
class Transaction:
    """Summary of a transaction described in the SAR."""

    date: Optional[str]
    amount: Optional[str]
    currency: Optional[str]
    originating_account: Optional[str]
    pass_through_accounts: List[str]
    beneficiaries: List[str]
    uetr: Optional[str]
    notes: Optional[str]


@dataclass
class SARData:
    """High level container for the parsed SAR information."""

    filing_type: Optional[str]
    filing_date: Optional[str]
    amendment_type: Optional[str]
    contact_office: Optional[str]
    contact_phone: Optional[str]
    contact_email: Optional[str]
    filer_name: Optional[str]
    subjects: List[Subject]
    transactions: List[Transaction]

    def to_dict(self) -> dict:
        """Return a JSON-serialisable representation of the SAR data."""

        return asdict(self)


def _collect_text_list(elements: Iterable[ET.Element]) -> List[str]:
    values: List[str] = []
    for element in elements:
        text = _text_or_none(element)
        if text:
            values.append(text)
    return values


class _SafeTreeBuilder(ET.TreeBuilder):
    """Tree builder that rejects DTD declarations and entity expansions."""

    def doctype(self, name, pubid, system):  # pragma: no cover - behaviour verified via parse_sar
        raise ValueError("DTD processing is disabled for SAR XML input")

    def entity(self, name):  # pragma: no cover - behaviour verified via parse_sar
        raise ValueError("Entity expansions are disabled for SAR XML input")


class _SafeXMLParser(ET.XMLParser):
    """XML parser that disables entity expansion and DTD processing."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("target", _SafeTreeBuilder())
        super().__init__(*args, **kwargs)
        parser = getattr(self, "parser", None)
        if parser is not None:
            try:
                parser.UseForeignDTD(False)
            except AttributeError:  # pragma: no cover - platform specific
                pass


def _safe_fromstring(xml_content: str) -> ET.Element:
    """Parse XML content using a hardened parser.

    ``defusedxml`` is preferred when available; otherwise, we fall back to a
    local parser that rejects DTD declarations and disables entity expansion.
    """

    if _DefusedET is not None:
        try:
            return _DefusedET.fromstring(xml_content)
        except _DEFUSED_SECURITY_ERRORS as exc:  # pragma: no cover - behaviour validated in tests
            raise ValueError(_SECURITY_ERROR_MESSAGE) from exc

    parser = _SafeXMLParser()
    try:
        return ET.fromstring(xml_content, parser=parser)
    except ValueError as exc:
        raise ValueError(_SECURITY_ERROR_MESSAGE) from exc


def parse_sar(xml_content: str) -> SARData:
    """Parse the provided SAR XML content into :class:`SARData`.

    Parameters
    ----------
    xml_content:
        The XML payload as a string.

    Returns
    -------
    SARData
        Structured representation of the key SAR components.
    """

    root = _safe_fromstring(xml_content)

    filing_info = root.find("f:FilingInformation", _NAMESPACE)
    filer_info = root.find("f:FilerInformation", _NAMESPACE)

    def filing(path: str) -> Optional[str]:
        return _text_or_none(filing_info.find(path, _NAMESPACE) if filing_info is not None else None)

    def filer(path: str) -> Optional[str]:
        return _text_or_none(filer_info.find(path, _NAMESPACE) if filer_info is not None else None)

    subjects: List[Subject] = []
    for subject_el in root.findall("f:Subjects/f:Subject", _NAMESPACE):
        subjects.append(
            Subject(
                name=_text_or_none(subject_el.find("f:Name", _NAMESPACE)),
                entity_type=_text_or_none(subject_el.find("f:EntityType", _NAMESPACE)),
            )
        )

    transactions: List[Transaction] = []
    for tx_el in root.findall("f:Transactions/f:Transaction", _NAMESPACE):
        amount_el = tx_el.find("f:Amount", _NAMESPACE)
        transactions.append(
            Transaction(
                date=_text_or_none(tx_el.find("f:Date", _NAMESPACE)),
                amount=_text_or_none(amount_el),
                currency=amount_el.get("currency") if amount_el is not None else None,
                originating_account=_text_or_none(tx_el.find("f:OriginatingAccount/f:Name", _NAMESPACE)),
                pass_through_accounts=_collect_text_list(
                    tx_el.findall("f:PassThroughAccounts/f:Account", _NAMESPACE)
                ),
                beneficiaries=_collect_text_list(
                    tx_el.findall("f:Beneficiaries/f:Beneficiary", _NAMESPACE)
                ),
                uetr=_text_or_none(tx_el.find("f:UETR", _NAMESPACE)),
                notes=_text_or_none(tx_el.find("f:Notes", _NAMESPACE)),
            )
        )

    return SARData(
        filing_type=filing("f:FilingType"),
        filing_date=filing("f:FilingDate"),
        amendment_type=filing("f:AmendmentType"),
        contact_office=filing("f:ContactOffice"),
        contact_phone=filing("f:ContactPhone"),
        contact_email=filing("f:ContactEmail"),
        filer_name=filer("f:FilerName"),
        subjects=subjects,
        transactions=transactions,
    )


def _cli(argv: List[str]) -> int:
    """Entry point for the module's CLI.

    Parameters
    ----------
    argv:
        Command line arguments excluding the executable name.
    """

    if not argv:
        print("Usage: sar_parser.py <path-to-sar-xml>", file=sys.stderr)
        return 1

    path = Path(argv[0])
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    sar_data = parse_sar(content)
    json.dump(sar_data.to_dict(), sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli(sys.argv[1:]))
