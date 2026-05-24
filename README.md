# Mini Ledger

A small data pipeline that reads CSV payment transactions, validates them,
converts amounts to CHF, and produces daily account aggregates.

---

## Requirements

- Python 3.11+
- pytest

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## How To Run

```bash
python main.py data/transactions.csv
```

---

## How To Run Tests

```bash
pytest tests/
```

---

## Project Structure

```
Mini_Ledger/
├── data/
│   └── transactions.csv
├── mini_ledger/
│   ├── models.py          # data classes and ReasonCode enum
│   ├── reader.py          # reads CSV -> raw dicts
│   ├── validator.py       # validates rows -> Transaction or DeadLetterRecord
│   ├── exchange_rate.py   # exchange rate provider
│   └── pipeline.py        # orchestrates all stages
├── tests/
│   ├── test_model.py
│   ├── test_reader.py
│   ├── test_validator.py
│   ├── test_exchange_rate.py
│   └── test_pipeline.py
├── main.py
└── README.md
```

---

## Assumptions

- Input is a CSV file passed as a command-line argument
- Exchange rates are hardcoded as per the specification
- Timestamp must be ISO-8601 format with Z suffix (UTC)
- Amount of zero is treated as invalid
- Negative amounts are valid
- If a valid transaction has no exchange rate available it is dead-lettered with MISSING_RATE
- Output is sorted by account_id and date for deterministic results
- If a row has multiple validation errors only the first detected error is reported

---

## Output

The program prints three sections to the console:

- **Daily Account Summaries** — total CHF per account per day
- **Dead Letters** — invalid records with reason codes
- **Metrics** — counts of total, valid, enriched, and invalid records