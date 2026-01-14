import subprocess
from pathlib import Path

PROJECT = Path("/mnt/c/sample alignment project")

def sh(cmd: str):
    print(">>", cmd)
    subprocess.run(cmd, shell=True, check=True)

def require(path: str):
    p = PROJECT / path
    if not p.exists():
        raise FileNotFoundError(f"Missing required file: {p}")

def main():
    # These scripts MUST exist (based on what you've built so far)
    require("scripts/02_run_fastqc.py")
    require("scripts/03_parse_fastqc.py")
    require("scripts/04_align_all.py")
    require("scripts/05_build_align_tables.py")
    require("scripts/06_make_final_tables.py")

    # Run steps (subsampling step is excluded because it may already be done / not scripted here)
    sh("python scripts/02_run_fastqc.py")
    sh("python scripts/03_parse_fastqc.py")
    sh("python scripts/04_align_all.py")
    sh("python scripts/05_build_align_tables.py")
    sh("python scripts/06_make_final_tables.py")

    print("Pipeline complete. Output: data/results/tables/final_report.csv")

if __name__ == '__main__':
    main()
