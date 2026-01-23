"""SAR XML parsing helpers."""

from __future__ import annotations

import os
from typing import Optional
from xml.etree import ElementTree as ET


class SarParseError(ValueError):
    """Raised when a SAR XML document cannot be parsed."""

    def __init__(self, message: str, *, location: Optional[str] = None) -> None:
        super().__init__(message)
        self.location = location


def parse_string(xml_text: str) -> ET.Element:
    """Parse a SAR document stored in memory."""

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:  # pragma: no cover - defensive path for malformed XML
        raise SarParseError(f"Malformed XML: {exc}.", location="/") from exc

    if root.tag != "SAR":
        raise SarParseError("Root element must be <SAR>.", location=f"/{root.tag}")

    return root


def parse_file(path: "str | os.PathLike[str] | os.PathLike[bytes] | int") -> ET.Element:
    """Load a SAR document from disk and parse its contents."""

    with open(path, "r", encoding="utf-8") as handle:
        xml_text = handle.read()
    return parse_string(xml_text)


__all__ = ["SarParseError", "parse_file", "parse_string"]
