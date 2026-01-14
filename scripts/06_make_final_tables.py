from pathlib import Path
import pandas as pd

PROJECT = Path("/mnt/c/sample alignment project")
TABLES = PROJECT / "data" / "results" / "tables"

qc = pd.read_csv(TABLES / "qc_metrics.csv")
tot = pd.read_csv(TABLES / "align_totals.csv")
byv = pd.read_csv(TABLES / "align_metrics_by_variant.csv")

# -----------------------------
# QC summary per sample
# -----------------------------
qc_summary = (
    qc.groupby(["sample_id", "status"])
      .size()
      .unstack(fill_value=0)
      .reset_index()
)
for col in ["PASS", "WARN", "FAIL"]:
    if col not in qc_summary.columns:
        qc_summary[col] = 0

qc_summary["qc_fail_rate"] = qc_summary["FAIL"] / (qc_summary["PASS"] + qc_summary["WARN"] + qc_summary["FAIL"])
qc_summary.to_csv(TABLES / "sample_qc_summary.csv", index=False)
print("Wrote:", TABLES / "sample_qc_summary.csv")

# -----------------------------
# Alignment summary per sample
# -----------------------------
# Use 'all' totals for mapping_rate, plus mapq30 totals
tot_all = tot[tot["filter"] == "all"].copy()
tot_q30 = tot[tot["filter"] == "mapq30"].copy()

align_summary = (
    tot_all.groupby("sample_id")[["total_reads", "total_mapped", "total_unmapped", "mapping_rate"]]
           .mean()
           .reset_index()
           .rename(columns={
               "total_reads": "avg_total_reads_all",
               "total_mapped": "avg_mapped_all",
               "total_unmapped": "avg_unmapped_all",
               "mapping_rate": "avg_mapping_rate_all"
           })
)

q30_summary = (
    tot_q30.groupby("sample_id")[["total_mapped", "mapping_rate"]]
           .mean()
           .reset_index()
           .rename(columns={
               "total_mapped": "avg_mapped_mapq30",
               "mapping_rate": "avg_mapping_rate_mapq30"
           })
)

align_summary = align_summary.merge(q30_summary, on="sample_id", how="left").fillna(0)

# -----------------------------
# Best reference variant per sample (using MAPQ30 mapped_per_mb as confidence)
# -----------------------------
byv_q30 = byv[byv["filter"] == "mapq30"].copy()

# mean mapped_per_mb across replicates per sample+variant
score = (
    byv_q30.groupby(["sample_id", "variant"])["mapped_per_mb"]
           .mean()
           .reset_index()
)

# pick best + second best to compute confidence gap
best = score.sort_values(["sample_id", "mapped_per_mb"], ascending=[True, False]).copy()
best["rank"] = best.groupby("sample_id").cumcount() + 1

best1 = best[best["rank"] == 1][["sample_id", "variant", "mapped_per_mb"]].rename(
    columns={"variant": "best_variant", "mapped_per_mb": "best_mapped_per_mb"}
)
best2 = best[best["rank"] == 2][["sample_id", "mapped_per_mb"]].rename(
    columns={"mapped_per_mb": "second_mapped_per_mb"}
)

align_summary = align_summary.merge(best1, on="sample_id", how="left")
align_summary = align_summary.merge(best2, on="sample_id", how="left")
align_summary["second_mapped_per_mb"] = align_summary["second_mapped_per_mb"].fillna(0)
align_summary["confidence_gap"] = align_summary["best_mapped_per_mb"] - align_summary["second_mapped_per_mb"]

# -----------------------------
# Classify samples
# -----------------------------
# Simple robust rule:
# if avg_mapping_rate_all < 0.01 => NO_MATCH
# else => MATCH
align_summary["classification"] = align_summary["avg_mapping_rate_all"].apply(
    lambda x: "NO_MATCH" if x < 0.01 else "MATCH"
)

align_summary.to_csv(TABLES / "sample_alignment_summary.csv", index=False)
print("Wrote:", TABLES / "sample_alignment_summary.csv")

# -----------------------------
# Final report (QC + alignment)
# -----------------------------
final = qc_summary.merge(align_summary, on="sample_id", how="left")
final.to_csv(TABLES / "final_report.csv", index=False)
print("Wrote:", TABLES / "final_report.csv")
