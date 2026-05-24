from datetime import datetime, timezone

import pytest
from mini_ledger.models import Transaction, DeadLetterRecord, EnrichedTransaction, DailyAccountSummary

@pytest.fixture
def valid_transaction() -> Transaction:
    return Transaction(
        txn_id='t1',
        account_id='A1',
        timestamp=datetime(2026, 4, 28, 10, 15, 0, tzinfo=timezone.utc),
        amount=100.00,
        currency='USD',
        merchant='Amazon',
        category='retail'
    )

def test_transaction_fields(valid_transaction:Transaction):
    assert valid_transaction.txn_id == 't1'
    assert valid_transaction.amount == 100.00

def test_dead_letter_fields():
    raw = {'txn_id': 't5', 'account_id': ''}
    record = DeadLetterRecord(raw_row=raw, reason_code='MISSING_ACCOUNT_ID')
    
    assert record.reason_code == 'MISSING_ACCOUNT_ID'
    assert record.raw_row == raw

def test_enriched_transaction_fields(valid_transaction:Transaction):
    test_amount = 90.00
    enriched_transaction = EnrichedTransaction(transaction=valid_transaction, amount_chf= test_amount)

    assert enriched_transaction.amount_chf == test_amount
    assert enriched_transaction.transaction.txn_id == "t1"


def test_daily_account_summary():
    summary = DailyAccountSummary(
        account_id="A1",
        date='2026-04-28',
        total_chf=140.00
    )

    assert summary.account_id == 'A1'
    assert summary.date == '2026-04-28'
    assert summary.total_chf == 140.00