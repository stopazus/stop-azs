"""Transaction data structures and normalization helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, MutableMapping, Optional


def _coerce_date(value: object) -> date:
    """Coerce common date representations into :class:`~datetime.date`."""

    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text).date()
    except ValueError as exc:  # pragma: no cover - defensive guard
        raise ValueError(f"Unsupported date format: {value}") from exc


@dataclass(frozen=True, slots=True)
class Transaction:
    """A normalized representation of a single escrow movement."""

    reference: str
    sender: str
    receiver: str
    amount: Decimal
    currency: str
    date: date
    invoice_number: Optional[str] = None
    destination_country: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: MutableMapping[str, object]) -> "Transaction":
        """Create an instance from a mapping."""

        def pop_any(mapping: MutableMapping[str, object], *keys: str) -> Optional[object]:
            for key in keys:
                if key in mapping:
                    value = mapping.pop(key)
                    if value is None:
                        continue
                    if isinstance(value, str):
                        value = value.strip()
                        if not value:
                            continue
                    return value
            return None

        raw = dict(raw)
        reference_value = pop_any(raw, "reference", "wire_reference", "ref", "id")
        if reference_value is None:
            raise ValueError("Transactions require a non-empty reference identifier")
        reference = str(reference_value).strip()
        if not reference:
            raise ValueError("Transactions require a non-empty reference identifier")

        sender_value = pop_any(raw, "sender", "originator", "from")
        receiver_value = pop_any(raw, "receiver", "beneficiary", "to")
        sender = str(sender_value).strip() if sender_value is not None else ""
        receiver = str(receiver_value).strip() if receiver_value is not None else ""
        if not sender or not receiver:
            raise ValueError("Transactions must specify both sender and receiver")

        raw_amount = pop_any(raw, "amount", "value")
        if raw_amount is None:
            raise ValueError("Transactions must include an amount")
        try:
            amount = Decimal(str(raw_amount))
        except InvalidOperation as exc:  # pragma: no cover - defensive guard
            raise ValueError(f"Could not parse amount '{raw_amount}'") from exc

        currency_value = pop_any(raw, "currency", "ccy")
        if currency_value is None:
            currency = "USD"
        else:
            currency = str(currency_value).strip().upper() or "USD"

        raw_date = pop_any(raw, "date", "timestamp", "posted_at")
        if raw_date is None:
            raise ValueError("Transactions must include a date")
        parsed_date = _coerce_date(raw_date)

        invoice_raw = pop_any(raw, "invoice_number", "invoice", "invoice_id")
        destination_raw = pop_any(raw, "country", "destination_country", "beneficiary_country")
        metadata: Dict[str, str] = {}
        excluded_metadata_keys = {"x-api-key"}
        for key, value in raw.items():
            if value is None:
                continue
            cleaned_key = str(key).strip() if isinstance(key, str) else str(key)
            if not cleaned_key:
                continue
            if cleaned_key.lower() in excluded_metadata_keys:
                continue
            if isinstance(value, str):
                cleaned_value = value.strip()
            else:
                cleaned_value = str(value).strip()
            if not cleaned_value:
                continue
            metadata[cleaned_key] = cleaned_value

        return cls(
            reference=reference,
            sender=sender,
            receiver=receiver,
            amount=amount,
            currency=currency,
            date=parsed_date,
            invoice_number=(str(invoice_raw).strip() or None) if invoice_raw is not None else None,
            destination_country=(
                str(destination_raw).strip().upper() or None
                if destination_raw is not None
                else None
            ),
            metadata=metadata,
        )

    def to_dict(self) -> Dict[str, object]:
        """Serialise the transaction back into a mapping."""

        base = {
            "reference": self.reference,
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": str(self.amount),
            "currency": self.currency,
            "date": self.date.isoformat(),
        }
        if self.invoice_number:
            base["invoice_number"] = self.invoice_number
        if self.destination_country:
            base["destination_country"] = self.destination_country
        base.update(self.metadata)
        return base


__all__ = ["Transaction"]
