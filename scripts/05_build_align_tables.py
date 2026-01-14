import csv
from pathlib import Path
import pandas as pd

PROJECT = Path("/mnt/c/sample alignment project")
ALIGN = PROJECT / "data" / "results" / "alignments"
OUT = PROJECT / "data" / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

variant_rows = []
total_rows = []

def parse_idxstats(idx_path: Path, sample: str, rep: int, filter_name: str):
    df = pd.read_csv(idx_path, sep="\t", header=None, names=["ref","length","mapped","unmapped"])
    star = df[df["ref"]=="*"]
    total_unmapped = int(star["unmapped"].iloc[0]) if len(star) else 0

    df2 = df[df["ref"]!="*"].copy()
    total_mapped = int(df2["mapped"].sum())
    total_reads = total_mapped + total_unmapped
    mapping_rate = (total_mapped / total_reads) if total_reads else 0.0

    # totals table row
    total_rows.append({
        "sample_id": sample,
        "replicate": rep,
        "filter": filter_name,
        "total_reads": total_reads,
        "total_mapped": total_mapped,
        "total_unmapped": total_unmapped,
        "mapping_rate": mapping_rate
    })

    # by-variant rows
    if total_mapped:
        df2["percent_of_mapped"] = df2["mapped"] / total_mapped * 100
    else:
        df2["percent_of_mapped"] = 0.0
    df2["mapped_per_mb"] = df2["mapped"] / (df2["length"] / 1_000_000)

    for _, r in df2.iterrows():
        variant_rows.append({
            "sample_id": sample,
            "replicate": rep,
            "filter": filter_name,
            "variant": r["ref"],
            "length": int(r["length"]),
            "mapped": int(r["mapped"]),
            "percent_of_mapped": float(r["percent_of_mapped"]),
            "mapped_per_mb": float(r["mapped_per_mb"])
        })

with open(PROJECT / "data" / "sample_sheet.csv", newline="") as f:
    for row in csv.DictReader(f):
        sample = row["sample_id"].strip()
        for rep in (1,2,3):
            base = ALIGN / sample / f"rep{rep}"
            idx_all = base / "idxstats_all.txt"
            idx_q30 = base / "idxstats_mapq30.txt"
            if idx_all.exists():
                parse_idxstats(idx_all, sample, rep, "all")
            if idx_q30.exists():
                parse_idxstats(idx_q30, sample, rep, "mapq30")

pd.DataFrame(variant_rows).to_csv(OUT / "align_metrics_by_variant.csv", index=False)
pd.DataFrame(total_rows).to_csv(OUT / "align_totals.csv", index=False)
print("Wrote:", OUT / "align_metrics_by_variant.csv")
print("Wrote:", OUT / "align_totals.csv")
