"""Transaction analysis utilities for SAR submissions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


REPEATED_INVOICE = "REPEATED_INVOICE"


@dataclass(frozen=True, slots=True)
class Transaction:
    sender: str
    invoice: str


def analyze_transactions(transactions: Iterable[Transaction]) -> list[set[str]]:
    """Return a list of flag codes per transaction in the input order."""

    invoice_senders: dict[str, set[str]] = {}
    ordered = list(transactions)
    for transaction in ordered:
        invoice_senders.setdefault(transaction.invoice, set()).add(transaction.sender)

    repeated_invoices = {
        invoice for invoice, senders in invoice_senders.items() if len(senders) > 1
    }

    flags: list[set[str]] = []
    for transaction in ordered:
        transaction_flags: set[str] = set()
        if transaction.invoice in repeated_invoices:
            transaction_flags.add(REPEATED_INVOICE)
        flags.append(transaction_flags)

    return flags
