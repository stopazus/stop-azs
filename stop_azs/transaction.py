"""Core data structures used throughout the project."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .utils import pop_any


DEFAULT_CURRENCY = "USD"
DEFAULT_DESCRIPTION = ""
DEFAULT_AMOUNT = 0


@dataclass(slots=True)
class Transaction:
    """Representation of a transaction payload.

    The class knows how to construct itself from a dictionary that may contain
    a variety of key aliases.  Historically :meth:`from_dict` treated any falsy
    value as an indication that a field was missing and immediately substituted
    defaults.  That behaviour incorrectly masked legitimate values such as the
    integer ``0`` or an empty string.  The implementation now only falls back
    to defaults when :func:`pop_any` explicitly returns ``None``.
    """

    amount: Any
    currency: str
    description: str
    notes: Any | None = None

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "Transaction":
        """Create a transaction from *payload*.

        Parameters
        ----------
        payload:
            A mapping containing transaction metadata.  The mapping is copied so
            that the caller's data remains unchanged.
        """

        working = dict(payload)

        amount = pop_any(working, ("amount", "value", "transaction_amount"))
        if amount is None:
            amount = DEFAULT_AMOUNT

        currency = pop_any(
            working,
            ("currency", "ccy", "transaction_currency"),
            default=DEFAULT_CURRENCY,
        )
        if currency is None:
            currency = DEFAULT_CURRENCY

        description = pop_any(
            working,
            ("description", "desc", "transaction_description"),
            default=DEFAULT_DESCRIPTION,
        )
        if description is None:
            description = DEFAULT_DESCRIPTION

        notes = pop_any(working, ("notes", "note"))

        return cls(amount=amount, currency=currency, description=description, notes=notes)
