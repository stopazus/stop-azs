"""Core utilities for screening escrow transactions.

The module purposefully keeps the detection heuristics simple: it surfaces
obvious anomalies so that human investigators can focus their time on the
most suspicious activity.  None of the rules are meant to be a definitive
statement of wrongdoing; they simply highlight patterns that *may* warrant a
closer look.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, MutableMapping, Optional, Sequence, Tuple
import csv
import json


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
        """Create an instance from a mapping.

        The function is intentionally forgiving: it understands a handful of
        common column names and stores unrecognised keys as metadata.  Values
        are coerced to strings where appropriate so the loader can deal with
        data exported from spreadsheets or banking portals.
        """

        def pop_any(mapping: MutableMapping[str, object], *keys: str) -> Optional[object]:
            for key in keys:
                if key in mapping and mapping[key] not in ("", None):
                    return mapping.pop(key)
            return None

        raw = dict(raw)
        reference_value = pop_any(raw, "reference", "wire_reference", "ref", "id")
        reference = str(reference_value).strip() if reference_value is not None else ""
        if not reference:
            raise ValueError("Transactions require a non-empty reference identifier")

        sender_value = pop_any(raw, "sender", "originator", "from")
        sender = str(sender_value).strip() if sender_value is not None else ""
        receiver_value = pop_any(raw, "receiver", "beneficiary", "to")
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
        currency = (
            str(currency_value).strip().upper() if currency_value is not None else ""
        ) or "USD"

        raw_date = pop_any(raw, "date", "timestamp", "posted_at")
        if raw_date is None:
            raise ValueError("Transactions must include a date")
        parsed_date = _coerce_date(raw_date)

        invoice_number = pop_any(raw, "invoice_number", "invoice", "invoice_id")
        destination_country = pop_any(raw, "country", "destination_country", "beneficiary_country")
        metadata = {key: str(value) for key, value in raw.items() if value not in (None, "")}

        return cls(
            reference=reference,
            sender=sender,
            receiver=receiver,
            amount=amount,
            currency=currency,
            date=parsed_date,
            invoice_number=str(invoice_number).strip() or None,
            destination_country=str(destination_country).strip().upper() if destination_country else None,
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


def _coerce_date(value: object) -> date:
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
class SuspicionFlag:
    """Represents a single heuristic that flagged a transaction."""

    code: str
    message: str
    details: Dict[str, object] = field(default_factory=dict)


class TransactionAnalyzer:
    """Apply a collection of heuristics to escrow transactions."""

    def __init__(
        self,
        *,
        large_amount_threshold: Decimal = Decimal("50000"),
        repeat_invoice_threshold: int = 2,
        domestic_country: Optional[str] = None,
        high_risk_countries: Optional[Sequence[str]] = None,
    ) -> None:
        if repeat_invoice_threshold < 1:
            raise ValueError("repeat_invoice_threshold must be at least 1")
        self.large_amount_threshold = large_amount_threshold
        self.repeat_invoice_threshold = repeat_invoice_threshold
        self.domestic_country = domestic_country.upper() if domestic_country else None
        self.high_risk_countries = {c.upper() for c in high_risk_countries} if high_risk_countries else set()

    def analyze(self, transactions: Iterable[Transaction]) -> List[Tuple[Transaction, List[SuspicionFlag]]]:
        tx_list = list(transactions)
        invoice_sender_counts: Dict[str, set[str]] = defaultdict(set)
        receiver_senders: Dict[str, set[str]] = defaultdict(set)
        for tx in tx_list:
            if tx.invoice_number:
                invoice_sender_counts[tx.invoice_number].add(tx.sender)
            receiver_senders[tx.receiver].add(tx.sender)

        results: List[Tuple[Transaction, List[SuspicionFlag]]] = []
        for tx in tx_list:
            flags: List[SuspicionFlag] = []
            if tx.amount >= self.large_amount_threshold:
                flags.append(
                    SuspicionFlag(
                        code="LARGE_AMOUNT",
                        message="Transfer amount exceeds the configured threshold",
                        details={"amount": str(tx.amount), "threshold": str(self.large_amount_threshold)},
                    )
                )

            if (
                tx.invoice_number
                and len(invoice_sender_counts[tx.invoice_number]) > self.repeat_invoice_threshold
            ):
                flags.append(
                    SuspicionFlag(
                        code="REPEATED_INVOICE",
                        message="Invoice number reused by multiple senders",
                        details={
                            "invoice_number": tx.invoice_number,
                            "unique_senders": len(invoice_sender_counts[tx.invoice_number]),
                            "threshold": self.repeat_invoice_threshold,
                        },
                    )
                )

            if self.domestic_country and tx.destination_country and tx.destination_country != self.domestic_country:
                flags.append(
                    SuspicionFlag(
                        code="CROSS_BORDER",
                        message="Funds routed to an international destination",
                        details={
                            "destination_country": tx.destination_country,
                            "domestic_country": self.domestic_country,
                        },
                    )
                )

            if self.high_risk_countries and tx.destination_country in self.high_risk_countries:
                flags.append(
                    SuspicionFlag(
                        code="HIGH_RISK_JURISDICTION",
                        message="Destination country is on the high-risk list",
                        details={"destination_country": tx.destination_country},
                    )
                )

            if len(receiver_senders[tx.receiver]) > self.repeat_invoice_threshold:
                flags.append(
                    SuspicionFlag(
                        code="MULTIPLE_SENDERS",
                        message="Receiver aggregates funds from numerous senders",
                        details={
                            "receiver": tx.receiver,
                            "unique_senders": len(receiver_senders[tx.receiver]),
                            "threshold": self.repeat_invoice_threshold,
                        },
                    )
                )

            results.append((tx, flags))
        return results


def load_transactions(path: str | Path, *, encoding: str = "utf-8") -> List[Transaction]:
    """Load transactions from a CSV or JSON document."""

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Cannot locate transaction file: {file_path}")

    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        with file_path.open("r", encoding=encoding, newline="") as handle:
            reader = csv.DictReader(handle)
            return [Transaction.from_dict(row) for row in reader]
    if suffix == ".ndjson":
        with file_path.open("r", encoding=encoding) as handle:
            return [
                Transaction.from_dict(json.loads(line))
                for line in handle
                if line.strip()
            ]
    if suffix == ".json":
        with file_path.open("r", encoding=encoding) as handle:
            data = json.load(handle)
        if isinstance(data, dict):
            data = data.get("transactions", [])
        if not isinstance(data, list):
            raise ValueError("JSON transaction payload must be a list")
        return [Transaction.from_dict(item) for item in data]

    raise ValueError("Unsupported file format. Expected CSV or JSON.")


def iter_flag_summary(results: Sequence[Tuple[Transaction, List[SuspicionFlag]]]) -> Iterator[Tuple[str, int]]:
    """Summarise the number of times each flag code appears."""

    counter: Counter[str] = Counter()
    for _, flags in results:
        counter.update(flag.code for flag in flags)
    for code, count in sorted(counter.items(), key=lambda item: (-item[1], item[0])):
        yield code, count
