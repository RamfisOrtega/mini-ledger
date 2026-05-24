from dataclasses import dataclass
from datetime import datetime

from enum import Enum

class ReasonCode(Enum):
    MISSING_TXN_ID      = "MISSING_TXN_ID"
    MISSING_ACCOUNT_ID  = "MISSING_ACCOUNT_ID"
    INVALID_TIMESTAMP   = "INVALID_TIMESTAMP"
    INVALID_AMOUNT      = "INVALID_AMOUNT"
    INVALID_CURRENCY    = "INVALID_CURRENCY"
    MISSING_RATE        = "MISSING_RATE"

@dataclass
class Transaction:
    txn_id: str
    account_id: str
    timestamp: datetime
    amount: float
    currency: str
    merchant: str
    category: str

@dataclass
class DeadLetterRecord:
    raw_row: dict
    reason_code: ReasonCode

@dataclass
class EnrichedTransaction:
    transaction: Transaction
    amount_chf: float

@dataclass
class DailyAccountSummary:
    account_id: str
    date: str
    total_chf: float