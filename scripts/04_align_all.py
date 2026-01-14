import csv
import subprocess
from pathlib import Path
import pandas as pd

PROJECT = Path("/mnt/c/sample alignment project")
SUB = PROJECT / "data" / "subsamples"
REF = PROJECT / "data" / "references" / "ecoli_3variants.fasta"
OUT_ALIGN = PROJECT / "data" / "results" / "alignments"
OUT_TABLES = PROJECT / "data" / "results" / "tables"
OUT_ALIGN.mkdir(parents=True, exist_ok=True)
OUT_TABLES.mkdir(parents=True, exist_ok=True)

THREADS = 4
MAPQ = 30

def sh(cmd: str):
    print(">>", cmd)
    subprocess.run(cmd, shell=True, check=True)

def idxstats_to_df(idx_path: Path, sample: str, rep: int, filter_name: str):
    df = pd.read_csv(idx_path, sep="\t", header=None, names=["variant","length","mapped","unmapped"])
    df = df[df["variant"] != "*"].copy()
    total = df["mapped"].sum()
    df["percent_of_mapped"] = (df["mapped"] / total * 100) if total else 0.0
    df["mapped_per_mb"] = df["mapped"] / (df["length"] / 1_000_000)
    df["sample_id"] = sample
    df["replicate"] = rep
    df["filter"] = filter_name
    return df

if not REF.exists():
    raise FileNotFoundError(f"Reference FASTA not found: {REF}")

rows = []

with open(PROJECT / "data" / "sample_sheet.csv", newline="") as f:
    for row in csv.DictReader(f):
        sample = row["sample_id"].strip()

        for rep in (1, 2, 3):
            r1 = SUB / sample / f"rep{rep}_1.fastq.gz"
            r2 = SUB / sample / f"rep{rep}_2.fastq.gz"
            if not r1.exists() or not r2.exists():
                raise FileNotFoundError(f"Missing subsample FASTQ for {sample} rep{rep}")

            run_dir = OUT_ALIGN / sample / f"rep{rep}"
            run_dir.mkdir(parents=True, exist_ok=True)

            sam = run_dir / "align.sam"
            bam = run_dir / "align.bam"
            sbam = run_dir / "align.sorted.bam"
            idx_all = run_dir / "idxstats_all.txt"

            # Align
            sh(f"bwa mem -t {THREADS} '{REF}' '{r1}' '{r2}' > '{sam}'")
            sh(f"samtools view -Sb '{sam}' -o '{bam}'")
            sh(f"samtools sort '{bam}' -o '{sbam}'")
            sh(f"samtools index '{sbam}'")
            sh(f"samtools idxstats '{sbam}' > '{idx_all}'")

            # MAPQ30 filter
            qbam = run_dir / f"align.mapq{MAPQ}.bam"
            qsbam = run_dir / f"align.mapq{MAPQ}.sorted.bam"
            idx_q = run_dir / f"idxstats_mapq{MAPQ}.txt"

            sh(f"samtools view -b -q {MAPQ} '{sbam}' > '{qbam}'")
            sh(f"samtools sort '{qbam}' -o '{qsbam}'")
            sh(f"samtools index '{qsbam}'")
            sh(f"samtools idxstats '{qsbam}' > '{idx_q}'")

            # Collect into table rows
            rows.append(idxstats_to_df(idx_all, sample, rep, "all"))
            rows.append(idxstats_to_df(idx_q, sample, rep, "mapq30"))

result = pd.concat(rows, ignore_index=True)
out_csv = OUT_TABLES / "align_metrics.csv"
result.to_csv(out_csv, index=False)
print(f"Wrote: {out_csv} ({len(result)} rows)")
