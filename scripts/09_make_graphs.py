from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

TABLES = Path("data/results/tables")
OUT = Path("data/results/graphs")
OUT.mkdir(parents=True, exist_ok=True)

def savefig(name: str):
    out = OUT / name
    plt.tight_layout()
    plt.savefig(out, dpi=200)
    plt.close()
    print("Wrote:", out)

def main():
    # -----------------------------
    # Load tables
    # -----------------------------
    final = pd.read_csv(TABLES / "final_report.csv")
    totals = pd.read_csv(TABLES / "align_totals.csv")
    byv = pd.read_csv(TABLES / "align_metrics_by_variant.csv")
    qc = pd.read_csv(TABLES / "sample_qc_summary.csv")

    # -----------------------------
    # Plot 1: Avg mapping rate (ALL) per sample
    # -----------------------------
    df1 = final.sort_values("avg_mapping_rate_all", ascending=False)
    plt.figure()
    plt.bar(df1["sample_id"], df1["avg_mapping_rate_all"])
    plt.title("Average Mapping Rate (ALL reads) per Sample")
    plt.xlabel("Sample")
    plt.ylabel("Avg mapping_rate_all")
    savefig("01_avg_mapping_rate_all.png")

    # -----------------------------
    # Plot 2: Avg mapping rate (MAPQ30) per sample
    # -----------------------------
    df2 = final.sort_values("avg_mapping_rate_mapq30", ascending=False)
    plt.figure()
    plt.bar(df2["sample_id"], df2["avg_mapping_rate_mapq30"])
    plt.title("Average Mapping Rate (MAPQ30) per Sample")
    plt.xlabel("Sample")
    plt.ylabel("Avg mapping_rate_mapq30")
    savefig("02_avg_mapping_rate_mapq30.png")

    # -----------------------------
    # Plot 3: QC FAIL count per sample
    # -----------------------------
    df3 = qc.sort_values("FAIL", ascending=False)
    plt.figure()
    plt.bar(df3["sample_id"], df3["FAIL"])
    plt.title("FastQC FAIL Counts per Sample")
    plt.xlabel("Sample")
    plt.ylabel("FAIL count")
    savefig("03_qc_fail_counts.png")

    # -----------------------------
    # Plot 4: QC fail rate vs mapping rate (ALL)
    # -----------------------------
    df4 = final.copy()
    plt.figure()
    plt.scatter(df4["qc_fail_rate"], df4["avg_mapping_rate_all"])
    for _, r in df4.iterrows():
        plt.annotate(r["sample_id"], (r["qc_fail_rate"], r["avg_mapping_rate_all"]))
    plt.title("QC Fail Rate vs Avg Mapping Rate (ALL)")
    plt.xlabel("QC fail rate")
    plt.ylabel("Avg mapping_rate_all")
    savefig("04_qc_fail_rate_vs_mapping.png")

    # -----------------------------
    # Plot 5: Replicate mapping rates (ALL) per sample
    # -----------------------------
    t_all = totals[totals["filter"] == "all"].copy()
    # Make a wide table: rows=samples, columns=replicates, values=mapping_rate
    wide = t_all.pivot_table(index="sample_id", columns="replicate", values="mapping_rate", aggfunc="mean")
    wide = wide.reindex(sorted(wide.index))
    plt.figure()
    for sample_id in wide.index:
        y = wide.loc[sample_id].values
        x = wide.columns.values
        plt.plot(x, y, marker="o", label=sample_id)
    plt.title("Mapping Rate (ALL) Across Replicates")
    plt.xlabel("Replicate")
    plt.ylabel("mapping_rate (ALL)")
    plt.legend()
    savefig("05_mapping_rate_replicates_all.png")

    # -----------------------------
    # Plot 6: Variant competition per sample (MAPQ30)
    # -----------------------------
    v_q30 = byv[byv["filter"] == "mapq30"].copy()
    # Average across replicates: sample_id x variant
    v_avg = (v_q30.groupby(["sample_id", "variant"])["mapped_per_mb"]
                  .mean()
                  .reset_index())
    # Plot one grouped bar chart per sample (separate file per sample for clarity)
    for sample_id, sub in v_avg.groupby("sample_id"):
        sub = sub.sort_values("mapped_per_mb", ascending=False)
        plt.figure()
        plt.bar(sub["variant"], sub["mapped_per_mb"])
        plt.title(f"Variant Competition (MAPQ30) — {sample_id}")
        plt.xlabel("Reference variant (contig)")
        plt.ylabel("Avg mapped_per_mb")
        plt.xticks(rotation=20, ha="right")
        savefig(f"06_variant_competition_mapq30_{sample_id}.png")

    # -----------------------------

if __name__ == "__main__":
    main()
