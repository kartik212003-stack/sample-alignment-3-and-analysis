import argparse
from pathlib import Path
import pandas as pd
import mysql.connector

TABLES = [
    "qc_metrics",
    "align_totals",
    "align_metrics_by_variant",
    "sample_qc_summary",
    "sample_alignment_summary",
    "final_report",
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--db", default="sample_alignment")
    args = ap.parse_args()

    base = Path("data/results/tables")

    conn = mysql.connector.connect(
        host=args.host,
        user=args.user,
        password=args.password,
        database=args.db
    )
    cur = conn.cursor()

    for table in TABLES:
        csv_path = base / f"{table}.csv"
        if not csv_path.exists():
            print(f"Skip missing: {csv_path}")
            continue

        df = pd.read_csv(csv_path)
        cur.execute(f"TRUNCATE TABLE {table}")

        cols = ",".join(df.columns)
        placeholders = ",".join(["%s"] * len(df.columns))
        sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"

        cur.executemany(sql, [tuple(x) for x in df.itertuples(index=False, name=None)])
        conn.commit()
        print(f"Loaded {len(df)} rows into {table}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
