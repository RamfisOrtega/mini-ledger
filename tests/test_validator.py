from datetime import datetime

import pytest
from mini_ledger.models import ReasonCode
from mini_ledger.validator import TransactionValidator

@pytest.fixture
def valid_raw_row() -> dict:
    return {
        "txn_id": "t1",
        "account_id": "A1",
        "timestamp": "2026-04-28T10:15:00Z",
        "amount": "100.00",
        "currency": "USD",
        "merchant": "Amazon",
        "category": "retail"
    }

@pytest.fixture
def validator() -> TransactionValidator:
    return TransactionValidator()


def test_txn_id_is_non_empty(validator: TransactionValidator, valid_raw_row: dict):
    result = validator.validate(valid_raw_row)
    assert result.txn_id == 't1'

def test_txn_id_empty_returns_dead_letter(validator: TransactionValidator, valid_raw_row: dict):
    valid_raw_row["txn_id"] = ""
    result = validator.validate(valid_raw_row)
    assert result.reason_code == ReasonCode.MISSING_TXN_ID

def test_account_id_is_non_empty(validator: TransactionValidator, valid_raw_row: dict):
    result = validator.validate(valid_raw_row)
    assert result.account_id == "A1"

def test_account_id_empty_returns_dead_letter(validator: TransactionValidator, valid_raw_row: dict):
    valid_raw_row["account_id"]=""
    result = validator.validate(valid_raw_row)
    assert result.reason_code == ReasonCode.MISSING_ACCOUNT_ID

def test_timestamp_is_iso8601_with_z_utc(validator: TransactionValidator, valid_raw_row: dict):
    result =  validator.validate(valid_raw_row)
    assert result.timestamp == datetime.fromisoformat("2026-04-28T10:15:00+00:00")

def test_timestamp_empty_returns_dead_letter(validator: TransactionValidator, valid_raw_row:dict):
    valid_raw_row["timestamp"]=""
    result = validator.validate(valid_raw_row)
    assert result.reason_code == ReasonCode.INVALID_TIMESTAMP

def test_timestamp_without_z_returns_dead_letter(validator: TransactionValidator, valid_raw_row:dict):
    valid_raw_row["timestamp"] = "2026-04-28T10:15:00"
    result = validator.validate(valid_raw_row)
    assert result.reason_code == ReasonCode.INVALID_TIMESTAMP

def test_amount_non_numeric_returns_dead_letter(validator: TransactionValidator, valid_raw_row:dict):
    valid_raw_row["amount"] = "abc"
    result = validator.validate(valid_raw_row)
    assert result.reason_code == ReasonCode.INVALID_AMOUNT

def test_amount_is_number(validator: TransactionValidator, valid_raw_row:dict):
    result = validator.validate(valid_raw_row)
    assert result.amount == 100.00

def test_amount_is_zero_returns_dead_letter(validator: TransactionValidator, valid_raw_row:dict):
    valid_raw_row["amount"] = "0"
    result = validator.validate(valid_raw_row)
    assert result.reason_code == ReasonCode.INVALID_AMOUNT

def test_negative_amount_is_valid(validator: TransactionValidator, valid_raw_row:dict):
    valid_raw_row["amount"] = "-50.00"
    result = validator.validate(valid_raw_row)
    assert result.amount == -50.00

def test_amount_empty_returns_dead_letter(validator: TransactionValidator, valid_raw_row:dict):
    valid_raw_row["amount"] = ""
    result = validator.validate(valid_raw_row)
    assert result.reason_code == ReasonCode.INVALID_AMOUNT

def test_currency_too_short_returns_dead_letter(validator: TransactionValidator, valid_raw_row:dict):
    valid_raw_row["currency"] = "US"
    result = validator.validate(valid_raw_row)
    assert result.reason_code == ReasonCode.INVALID_CURRENCY

def test_currency_is_3_letter_code(validator: TransactionValidator, valid_raw_row:dict):
    result = validator.validate(valid_raw_row)
    assert result.currency == "USD"

def test_currency__empty_returns_dead_letter(validator: TransactionValidator, valid_raw_row:dict):
    valid_raw_row["currency"]= ""
    result = validator.validate(valid_raw_row)
    assert result.reason_code == ReasonCode.INVALID_CURRENCY

def test_currency_too_long_returns_dead_letter(validator: TransactionValidator, valid_raw_row:dict):
    valid_raw_row["currency"] = "USDX"
    result = validator.validate(valid_raw_row)
    assert result.reason_code == ReasonCode.INVALID_CURRENCY