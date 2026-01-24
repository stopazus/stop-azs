"""Core transaction analysis heuristics."""

from __future__ import annotations

from collections import Counter, defaultdict
from decimal import Decimal
from typing import Dict, Iterable, Iterator, List, Sequence, Tuple

from .flags import SuspicionFlag
from .transaction import Transaction


class TransactionAnalyzer:
    """Apply a collection of heuristics to escrow transactions."""

    def __init__(
        self,
        *,
        large_amount_threshold: Decimal = Decimal("50000"),
        repeat_invoice_threshold: int = 2,
        domestic_country: str | None = None,
        high_risk_countries: Sequence[str] | None = None,
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


def iter_flag_summary(results: Sequence[Tuple[Transaction, List[SuspicionFlag]]]) -> Iterator[Tuple[str, int]]:
    """Summarise the number of times each flag code appears."""

    counter: Counter[str] = Counter()
    for _, flags in results:
        counter.update(flag.code for flag in flags)
    for code, count in sorted(counter.items(), key=lambda item: (-item[1], item[0])):
        yield code, count


__all__ = ["TransactionAnalyzer", "iter_flag_summary"]
