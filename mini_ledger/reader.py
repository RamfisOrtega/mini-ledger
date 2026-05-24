import csv

from mini_ledger.models import Transaction


class TransactionReader:

    def read(self, file_path: str) -> list[dict]:
        rows = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(dict(row))
        return rows
