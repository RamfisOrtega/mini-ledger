from mini_ledger.exchange_rate import HardcodedRateProvider
from mini_ledger.models import DailyAccountSummary, DeadLetterRecord, EnrichedTransaction, ReasonCode, Transaction
from mini_ledger.validator import TransactionValidator
from mini_ledger.reader import TransactionReader

from collections import defaultdict

class Pipeline:

    def __init__(self):
        self.validator = TransactionValidator()
        self.rate_provider = HardcodedRateProvider()
        self.reader = TransactionReader()

    def _process_row(self, row: dict) -> Transaction | DeadLetterRecord:
        return self.validator.validate(row)
    
    def _enrich_row(self, transaction: Transaction) -> EnrichedTransaction | DeadLetterRecord:
            date = transaction.timestamp.strftime('%Y-%m-%d')
            rate = self.rate_provider.get_rate(transaction.currency, date)
            
            if rate is None:
                return DeadLetterRecord(transaction.__dict__, ReasonCode.MISSING_RATE)
            return EnrichedTransaction(transaction=transaction, amount_chf=transaction.amount * rate)
    
    def _aggregate(self, enriched: list[EnrichedTransaction]) -> list[DailyAccountSummary]:
        # defaultdict saves seeding each key before we add to it
        totals = defaultdict(float)

        for e in enriched:
             account_id = e.transaction.account_id
             txn_date = e.transaction.timestamp.strftime('%Y-%m-%d')
             totals[(account_id, txn_date)] += e.amount_chf
        
        result = []
        for (account_id, txn_date), total in totals.items():
             result.append(
                  DailyAccountSummary(account_id=account_id, date= txn_date, total_chf= total)
                  )
         
        return result
    

    def run(self, file_path: str) -> tuple[list[DailyAccountSummary], list[DeadLetterRecord], dict]:
        transactions_list = []
        enriched_list = []
        daily_summaries_list = []
        deadLetterRecord_list = []

        # Pull the raw rows off disk.
        records_list = self.reader.read(file_path)
        # A row either becomes a Transaction or gets set aside with a reason code.
        for record in records_list:
             record_object = self._process_row(record)
             if isinstance(record_object, DeadLetterRecord):
                  deadLetterRecord_list.append(record_object)
             elif isinstance(record_object, Transaction):
                  transactions_list.append(record_object)
             
        # Convert to CHF. A currency with no rate for that day is set aside too,
        # since one missing rate shouldn't sink the whole run.
        if transactions_list:
             for txn in transactions_list:
                  result = self._enrich_row(txn)
                  if isinstance(result, DeadLetterRecord):
                       deadLetterRecord_list.append(result)
                  elif isinstance(result, EnrichedTransaction):
                       enriched_list.append(result)
        

        # Roll up whatever survived, per account per day.
        if enriched_list:
             daily_summaries_list = self._aggregate(enriched_list)

        # Counted at the end so the numbers can't drift from the lists above.
        metrics = {
            "total_processed": len(records_list),
            "valid": len(transactions_list),
            "enriched": len(enriched_list),
            "invalid": len(deadLetterRecord_list)
        }
        
        return daily_summaries_list, deadLetterRecord_list, metrics