"""Utility helpers for analyzing escrow transactions.

The package exposes the :class:`~stop_azs.analyzer.TransactionAnalyzer` class
as a convenience import.
"""

from .analyzer import Transaction, TransactionAnalyzer, SuspicionFlag, load_transactions

__all__ = [
    "Transaction",
    "TransactionAnalyzer",
    "SuspicionFlag",
    "load_transactions",
]
