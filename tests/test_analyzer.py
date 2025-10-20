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
    flagged = [flags for _, flags in results if flags]
    assert flagged, "At least one transaction should be flagged"
    assert any(flag.code == "REPEATED_INVOICE" for flag in flagged[0])


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


def test_transaction_accepts_numeric_identifiers():
    tx = Transaction.from_dict(
        {
            "reference": 0,
            "sender": "Origin", 
            "receiver": "Recipient",
            "amount": 1500,
            "currency": "usd",
            "date": "2023-07-06",
            "invoice_number": 0,
        }
    )

    assert tx.reference == "0"
    assert tx.invoice_number == "0"


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
