import datetime

from mini_ledger.models import DeadLetterRecord, ReasonCode, Transaction
import re

class TransactionValidator:

    def validate(self, raw_row: dict) -> Transaction | DeadLetterRecord:
        amount = raw_row.get("amount")
        currency = raw_row.get("currency")
        timestamp = raw_row.get("timestamp")

        parsed_amount = self._parse_amount(amount)

        is_3letters = lambda ch: len(ch) == 3 and ch.isalpha()


        if not raw_row.get("txn_id"):
            return DeadLetterRecord(raw_row, ReasonCode.MISSING_TXN_ID)
        elif not raw_row.get("account_id"):
            return DeadLetterRecord(raw_row, ReasonCode.MISSING_ACCOUNT_ID)
        elif not timestamp or "Z" not in timestamp:
            return DeadLetterRecord(raw_row, ReasonCode.INVALID_TIMESTAMP)
        elif parsed_amount is None or parsed_amount == 0:
            return DeadLetterRecord(raw_row, ReasonCode.INVALID_AMOUNT)
        elif not is_3letters(currency):
            return DeadLetterRecord(raw_row, ReasonCode.INVALID_CURRENCY)
        else:
            return Transaction(**{
                **raw_row,
                "amount": parsed_amount,  # reuse, don't call again
                "timestamp": self._parse_timestamp(raw_row["timestamp"])
            })
            
        
    
    def _parse_timestamp(self, timestamp: str) -> datetime:
        return datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))


    def _parse_amount(self, amount) -> float | None:
        try:
            return float(amount)
        except (ValueError, TypeError):
            return None
        