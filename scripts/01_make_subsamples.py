import csv
import subprocess
from pathlib import Path

# Start modestly for speed. You can increase later.
N_READS = 200000
SEEDS = [101, 102, 103]

PROJECT = Path("/mnt/c/sample alignment project")
RAW = PROJECT / "data" / "raw_fastq"
SUB = PROJECT / "data" / "subsamples"
SUB.mkdir(parents=True, exist_ok=True)

def sh(cmd: str):
    print(">>", cmd)
    subprocess.run(cmd, shell=True, check=True)

with open(PROJECT / "data" / "sample_sheet.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        sample = row["sample_id"].strip()

        r1 = RAW / sample / f"{sample}_1.fastq.gz"
        r2 = RAW / sample / f"{sample}_2.fastq.gz"
        if not r1.exists() or not r2.exists():
            raise FileNotFoundError(f"Missing FASTQ for {sample}: {r1} or {r2}")

        outdir = SUB / sample
        outdir.mkdir(parents=True, exist_ok=True)

        for i, seed in enumerate(SEEDS, start=1):
            out1 = outdir / f"rep{i}_1.fastq.gz"
            out2 = outdir / f"rep{i}_2.fastq.gz"
            sh(f"seqtk sample -s{seed} '{r1}' {N_READS} | pigz -c > '{out1}'")
            sh(f"seqtk sample -s{seed} '{r2}' {N_READS} | pigz -c > '{out2}'")

print("Done: subsamples created for all samples.")
