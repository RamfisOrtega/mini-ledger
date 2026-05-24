import sys

from mini_ledger.pipeline import Pipeline

def main():
    
    if len(sys.argv) < 2:
        print("Error: Please provide at least one argument.")
        sys.exit(1)
    
    file_path = sys.argv[1]

    pipeline = Pipeline()
    daily_summaries_list, deadLetterRecord_list, metrics = pipeline.run(file_path)

    print("\n======== DAILY ACCOUNT SUMMARIES ========")
    print(f"{'account_id':<12} {'date':<12} {'total_chf':>12}")
    print("-" * 38)

    key = lambda x: (x.account_id, x.date)

    for s in sorted(daily_summaries_list, key=key):
        print(f"{s.account_id:<12} {s.date:<12} {s.total_chf:>12.2f}")

    print("\n======== DEAD LETTERS ========")
    print(f"{'txn_id':<10} {'reason_code':<25}")
    print("-" * 35)

    for d in deadLetterRecord_list:
        txn_id = d.raw_row.get('txn_id', 'N/A')
        print(f"{txn_id:<10} {d.reason_code.value:<25}")

    print("\n======== METRICS ========")
    for key, value in metrics.items():
        print(f"{key:<20}: {value}")

    print("\n")

if __name__ == "__main__":
    main()