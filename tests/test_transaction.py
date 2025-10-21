import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from stop_azs.transaction import Transaction


def test_from_dict_retains_falsy_values():
    payload = {
        "amount": 0,
        "currency": "",
        "description": "",
        "notes": False,
    }

    transaction = Transaction.from_dict(payload)

    assert transaction.amount == 0
    assert transaction.currency == ""
    assert transaction.description == ""
    assert transaction.notes is False


def test_from_dict_uses_defaults_only_for_missing_values():
    payload = {}

    transaction = Transaction.from_dict(payload)

    assert transaction.amount == 0
    assert transaction.currency == "USD"
    assert transaction.description == ""
    assert transaction.notes is None
