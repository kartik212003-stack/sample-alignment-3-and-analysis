import argparse
from pathlib import Path
import pandas as pd
import mysql.connector

QUERIES = {
    "final_report": """
        SELECT * FROM final_report ORDER BY avg_mapping_rate_all DESC;
    """,
    "no_match_samples": """
        SELECT sample_id, avg_mapping_rate_all, avg_mapping_rate_mapq30, classification
        FROM sample_alignment_summary
        WHERE classification='NO_MATCH'
        ORDER BY avg_mapping_rate_all;
    """,
    "variant_competition_mapq30": """
        SELECT sample_id, variant,
               AVG(percent_of_mapped) AS avg_percent_of_mapped,
               AVG(mapped_per_mb) AS avg_mapped_per_mb
        FROM align_metrics_by_variant
        WHERE filter='mapq30'
        GROUP BY sample_id, variant
        ORDER BY sample_id, avg_mapped_per_mb DESC;
    """,
    "qc_failures": """
        SELECT sample_id, test, COUNT(*) AS fail_count
        FROM qc_metrics
        WHERE status='FAIL'
        GROUP BY sample_id, test
        ORDER BY sample_id, fail_count DESC;
    """,
    "qc_vs_mapping": """
        SELECT q.sample_id, q.FAIL, q.qc_fail_rate, a.avg_mapping_rate_all, a.classification
        FROM sample_qc_summary q
        JOIN sample_alignment_summary a USING(sample_id)
        ORDER BY a.avg_mapping_rate_all DESC;
    """,
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--db", default="sample_alignment")
    args = ap.parse_args()

    outdir = Path("data/results/sql_outputs")
    outdir.mkdir(parents=True, exist_ok=True)

    conn = mysql.connector.connect(
        host=args.host,
        user=args.user,
        password=args.password,
        database=args.db
    )

    for name, sql in QUERIES.items():
        df = pd.read_sql(sql, conn)
        out = outdir / f"{name}.csv"
        df.to_csv(out, index=False)
        print(f"Wrote: {out} ({len(df)} rows)")

    conn.close()

if __name__ == "__main__":
    main()
