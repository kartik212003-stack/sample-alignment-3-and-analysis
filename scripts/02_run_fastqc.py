import csv
import subprocess
from pathlib import Path

PROJECT = Path("/mnt/c/sample alignment project")
SUB = PROJECT / "data" / "subsamples"
OUT = PROJECT / "data" / "results" / "fastqc"
OUT.mkdir(parents=True, exist_ok=True)

def run(cmd):
    print(">>", " ".join(cmd))
    subprocess.run(cmd, check=True)

with open(PROJECT / "data" / "sample_sheet.csv", newline="") as f:
    for row in csv.DictReader(f):
        sample = row["sample_id"].strip()
        outdir = OUT / sample
        outdir.mkdir(parents=True, exist_ok=True)

        for rep in (1, 2, 3):
            r1 = SUB / sample / f"rep{rep}_1.fastq.gz"
            r2 = SUB / sample / f"rep{rep}_2.fastq.gz"

            if not r1.exists() or not r2.exists():
                raise FileNotFoundError(f"Missing subsample files for {sample} rep{rep}")

            run(["fastqc", "-o", str(outdir), str(r1), str(r2)])

print("Done: FastQC finished for all samples/replicates.")
