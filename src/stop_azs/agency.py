"""Data structures describing agency contacts."""

from __future__ import annotations

from dataclasses import dataclass
import re


_SLUG_PATTERN = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class AgencyContact:
    """Representation of an agency contact for a submission package."""

    agency: str
    program: str
    reference: str | None = None

    def slug(self) -> str:
        """Return a filesystem-friendly slug derived from the agency and program.

        The slug is lowercase, ASCII-only, and composed of alphanumeric characters
        separated by hyphens. Consecutive separators collapse into a single hyphen.
        """

        raw = f"{self.agency}-{self.program}"
        lowered = raw.lower()
        slug = _SLUG_PATTERN.sub("-", lowered).strip("-")
        return slug or "agency"

    def formatted_block(self) -> str:
        """Render the contact details as a Markdown block."""

        lines = [f"**Agency:** {self.agency}", f"**Program:** {self.program}"]
        if self.reference:
            lines.append(f"**Reference:** {self.reference}")
        return "\n".join(lines)
