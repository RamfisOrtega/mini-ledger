from datetime import datetime, timezone

import pytest
from mini_ledger.pipeline import Pipeline
from mini_ledger.models import ReasonCode, Transaction, DeadLetterRecord, EnrichedTransaction, DailyAccountSummary

@pytest.fixture
def pipeline():                                   
    return Pipeline()

@pytest.fixture
def valid_raw_rows() -> list[dict]:
    return [
        {"txn_id": "t1", "account_id": "A1", "timestamp": "2026-04-28T10:15:00Z", "amount": "100.00", "currency": "USD", "merchant": "Amazon", "category": "retail"},
        {"txn_id": "t2", "account_id": "A1", "timestamp": "2026-04-28T11:00:00Z", "amount": "50.00", "currency": "CHF", "merchant": "Coop", "category": "groceries"},
        {"txn_id": "t3", "account_id": "A2", "timestamp": "2026-04-29T09:30:00Z", "amount": "80.00", "currency": "EUR", "merchant": "UBS", "category": "banking"},
    ]

@pytest.fixture
def invalid_raw_rows() -> list[dict]:
    return [
        {"txn_id": "t5", "account_id": "", "timestamp": "2026-04-29T12:10:00Z", "amount": "10.00", "currency": "CHF", "merchant": "Migros", "category": "groceries"},
        {"txn_id": "t6", "account_id": "A1", "timestamp": "2026-04-28T12:30:00Z", "amount": "0", "currency": "CHF", "merchant": "Coop", "category": "groceries"},
        {"txn_id": "t14", "account_id": "A4", "timestamp": "2026-04-28T10:00:00Z", "amount": "abc", "currency": "CHF", "merchant": "Coop", "category": "groceries"},
        {"txn_id": "t15", "account_id": "A4", "timestamp": "2026-04-28T10:00:00Z", "amount": "75.00", "currency": "US", "merchant": "Nike", "category": "retail"},
        {"txn_id": "t18", "account_id": "A5", "timestamp": "2026-04-28T10:15:00", "amount": "90.00", "currency": "CHF", "merchant": "Migros", "category": "groceries"},
        {"txn_id": "t20", "account_id": "", "timestamp": "", "amount": "", "currency": "", "merchant": "", "category": ""},
    ]

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

@pytest.fixture
def gbp_transaction() -> Transaction:
    return Transaction(
        txn_id='t4',
        account_id='A2',
        timestamp=datetime(2026, 4, 29, 12, 0, 0, tzinfo=timezone.utc),
        amount=12.00,
        currency='GBP',
        merchant='Tesco',
        category='retail'
    )

@pytest.fixture
def enriched_same_account_same_date() -> list[EnrichedTransaction]: # For the _aggregate_groups_by_account_and_date test
    t1 = Transaction(
        txn_id='t1', account_id='A1',
        timestamp=datetime(2026, 4, 28, 10, 15, 0, tzinfo=timezone.utc),
        amount=100.00, currency='USD', merchant='Amazon', category='retail'
    )
    t2 = Transaction(
        txn_id='t2', account_id='A1',
        timestamp=datetime(2026, 4, 28, 11, 0, 0, tzinfo=timezone.utc),
        amount=50.00, currency='CHF', merchant='Coop', category='groceries'
    )
    return [
        EnrichedTransaction(transaction=t1, amount_chf=90.00),   # 100 * 0.90
        EnrichedTransaction(transaction=t2, amount_chf=50.00),   # 50 * 1.00
    ]

def test_pipeline_valid_rows_become_transactions(pipeline: Pipeline, valid_raw_rows: list[dict]):
   for row in valid_raw_rows:
       result = pipeline._process_row(row)
       assert isinstance(result, Transaction)
    

def test_pipeline_invalid_rows_become_dead_letters(pipeline: Pipeline, invalid_raw_rows: list[dict]):
    for row in invalid_raw_rows:
        result = pipeline._process_row(row)
        assert isinstance(result, DeadLetterRecord)

def test_pipeline_enriched_transactions_have_chf_amount(pipeline: Pipeline, valid_transaction: Transaction):
    result = pipeline._enrich_row(valid_transaction) # return this type: EnrichedTransaction
    valid_usd_exchange_rate = 0.90
    correct_value = valid_transaction.amount * valid_usd_exchange_rate

    assert result.amount_chf == correct_value
    

def test_pipeline_aggregate_groups_by_account_and_date(pipeline: Pipeline, enriched_same_account_same_date: list[EnrichedTransaction]):
    total_test_amount_chf = 140
    enriched_list = enriched_same_account_same_date
    result = pipeline._aggregate(enriched_list)
    assert len(result) == 1
    assert result[0].total_chf == total_test_amount_chf

def test_pipeline_missing_rate_goes_to_dead_letter(pipeline: Pipeline, gbp_transaction: Transaction):
    result = pipeline._enrich_row(gbp_transaction)
    assert isinstance(result, DeadLetterRecord)
    assert result.reason_code == ReasonCode.MISSING_RATE

def test_pipeline_returns_daily_summaries(pipeline: Pipeline):
    daily_summaries_list, _, _ = pipeline.run("data/transactions.csv") # only captures the daily summaries list
    assert len(daily_summaries_list)> 1
    

def test_pipeline_correct_total_chf_for_account(pipeline: Pipeline):
    daily_summaries_list, _, _ = pipeline.run("data/transactions.csv")
    # find A1 on 2026-04-28
    
    is_a1 = lambda s: s.account_id =="A1"
    is_target_date = lambda s: s.date == "2026-04-28"

    a1 = next(s for s in daily_summaries_list if is_a1 and is_target_date)

    assert a1.total_chf == 315.00
    

def test_pipeline_dead_letters_collected(pipeline: Pipeline):
    _, deadLetterRecord_list, _ = pipeline.run("data/transactions.csv")
    assert len(deadLetterRecord_list)> 1

def test_pipeline_metrics_counts_are_correct(pipeline: Pipeline):
    _, _, metrics = pipeline.run("data/transactions.csv")
    assert metrics["total_processed"] == 25
    assert metrics["valid"] == 16
    assert metrics["enriched"] == 13
    assert metrics["invalid"] == 12