import pytest

from mini_ledger.reader import TransactionReader

@pytest.fixture
def reader():
    return TransactionReader()

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

file_path = "data/transactions.csv"

def test_read_returns_list_of_dicts(reader: TransactionReader, valid_raw_row: dict):
    result = reader.read(file_path)
    assert result[0] == valid_raw_row


def test_read_correct_number_of_rows(reader: TransactionReader):
    result = reader.read(file_path)
    assert len(result) == 25

def test_read_row_contains_expected_fields(reader: TransactionReader):
    result = reader.read(file_path)
    assert set(result[0].keys()) == {"txn_id", "account_id", "timestamp", "amount", "currency", "merchant", "category"}