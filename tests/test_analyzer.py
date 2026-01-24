from decimal import Decimal
from datetime import date

import pytest

from stop_azs.analyzer import Transaction, TransactionAnalyzer, iter_flag_summary


def make_transaction(**overrides):
    base = {
        "reference": "REF-1",
        "sender": "Sender A",
        "receiver": "Receiver B",
        "amount": Decimal("25000"),
        "currency": "USD",
        "date": date(2023, 7, 6),
    }
    base.update(overrides)
    return Transaction(**base)


def test_large_amount_flagged():
    tx = make_transaction(amount=Decimal("100000"))
    analyzer = TransactionAnalyzer(large_amount_threshold=Decimal("50000"))
    results = analyzer.analyze([tx])
    assert len(results[0][1]) == 1
    assert results[0][1][0].code == "LARGE_AMOUNT"


def test_repeated_invoice_counts_unique_senders():
    txs = [
        make_transaction(reference="REF-1", invoice_number="INV-10", sender="A"),
        make_transaction(reference="REF-2", invoice_number="INV-10", sender="B"),
        make_transaction(reference="REF-3", invoice_number="INV-10", sender="C"),
    ]
    analyzer = TransactionAnalyzer(repeat_invoice_threshold=2)
    results = analyzer.analyze(txs)
    for tx, flags in results:
        if tx.invoice_number == "INV-10":
            codes = {flag.code for flag in flags}
            assert "REPEATED_INVOICE" in codes
            repeated_flag = next(flag for flag in flags if flag.code == "REPEATED_INVOICE")
            assert repeated_flag.details["unique_senders"] == 3
            assert repeated_flag.details["threshold"] == 2


def test_cross_border_and_high_risk_flags():
    tx = make_transaction(destination_country="GB", reference="REF-4")
    analyzer = TransactionAnalyzer(domestic_country="US", high_risk_countries=["GB"])
    results = analyzer.analyze([tx])
    codes = {flag.code for flag in results[0][1]}
    assert codes == {"CROSS_BORDER", "HIGH_RISK_JURISDICTION"}


def test_iter_flag_summary_orders_by_count_then_code():
    tx1 = make_transaction(reference="REF-5", amount=Decimal("75000"))
    tx2 = make_transaction(reference="REF-6", amount=Decimal("99000"))
    analyzer = TransactionAnalyzer(large_amount_threshold=Decimal("50000"))
    results = analyzer.analyze([tx1, tx2])
    summary = list(iter_flag_summary(results))
    assert summary == [("LARGE_AMOUNT", 2)]


def test_transaction_to_dict_round_trips_metadata():
    tx = make_transaction(metadata={"wire_reference": "ABC", "notes": "urgent"})
    serialized = tx.to_dict()
    assert serialized["notes"] == "urgent"
    assert serialized["wire_reference"] == "ABC"
    # Ensure required fields are still present
    assert serialized["reference"] == tx.reference


def test_transaction_requires_reference_sender_receiver():
    with pytest.raises(ValueError):
        Transaction.from_dict({})


def test_transaction_from_dict_accepts_numeric_reference():
    tx = Transaction.from_dict(
        {
            "reference": 0,
            "sender": "Sender",
            "receiver": "Receiver",
            "amount": "250.00",
            "currency": "usd",
            "date": "2023-07-06",
        }
    )
    assert tx.reference == "0"


def test_transaction_from_dict_trims_optional_fields_and_metadata():
    tx = Transaction.from_dict(
        {
            "reference": "  REF-7  ",
            "sender": "  Sender  ",
            "receiver": "Receiver",
            "amount": " 250.00 ",
            "currency": " usd ",
            "date": " 2023-07-06 ",
            "invoice": "  INV-99  ",
            "destination_country": " gb ",
            " note ": "  urgent  ",
        }
    )
    assert tx.reference == "REF-7"
    assert tx.currency == "USD"
    assert tx.invoice_number == "INV-99"
    assert tx.destination_country == "GB"
    assert tx.metadata["note"] == "urgent"


def test_load_transactions_from_csv(tmp_path):
    csv_content = "reference,sender,receiver,amount,currency,date\nREF-1,A,B,1000,USD,2023-07-06\n"
    path = tmp_path / "tx.csv"
    path.write_text(csv_content)
    from stop_azs.analyzer import load_transactions

    items = load_transactions(path)
    assert len(items) == 1
    assert items[0].reference == "REF-1"


def test_load_transactions_from_ndjson(tmp_path):
    ndjson_content = '{"reference":"REF-1","sender":"A","receiver":"B","amount":1000,"currency":"USD","date":"2023-07-06"}\n'
    path = tmp_path / "tx.ndjson"
    path.write_text(ndjson_content)
    from stop_azs.analyzer import load_transactions

    items = load_transactions(path)
    assert len(items) == 1
    assert items[0].reference == "REF-1"
