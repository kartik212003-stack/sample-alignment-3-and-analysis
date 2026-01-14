import csv
import zipfile
from pathlib import Path
import pandas as pd

PROJECT = Path("/mnt/c/sample alignment project")
QC_DIR = PROJECT / "data" / "results" / "fastqc"
OUT_DIR = PROJECT / "data" / "results" / "tables"
OUT_DIR.mkdir(parents=True, exist_ok=True)

rows = []

with open(PROJECT / "data" / "sample_sheet.csv", newline="") as f:
    for row in csv.DictReader(f):
        sample = row["sample_id"].strip()
        sample_qc = QC_DIR / sample

        for rep in (1, 2, 3):
            for mate in (1, 2):
                zip_path = sample_qc / f"rep{rep}_{mate}_fastqc.zip"
                if not zip_path.exists():
                    raise FileNotFoundError(f"Missing FastQC zip: {zip_path}")

                with zipfile.ZipFile(zip_path) as z:
                    # Find the summary file inside the zip
                    summary_files = [n for n in z.namelist() if n.endswith("summary.txt")]
                    if not summary_files:
                        raise RuntimeError(f"No summary.txt found in {zip_path}")
                    summary_name = summary_files[0]

                    text = z.read(summary_name).decode("utf-8", errors="replace")

                for line in text.strip().splitlines():
                    # Format: STATUS \t TEST \t FILENAME
                    status, test, filename = line.split("\t")
                    rows.append({
                        "sample_id": sample,
                        "replicate": rep,
                        "mate": mate,
                        "test": test,
                        "status": status,
                        "fastq_file": filename
                    })

df = pd.DataFrame(rows)
out_csv = OUT_DIR / "qc_metrics.csv"
df.to_csv(out_csv, index=False)
print(f"Wrote: {out_csv} ({len(df)} rows)")
