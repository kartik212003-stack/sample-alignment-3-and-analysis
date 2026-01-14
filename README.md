# Sample Alignment Project (WGS QC + Strain Matching) — Python + SQL

Automated pipeline for paired-end FASTQ samples:
- replicate subsampling (rep1–rep3)
- FastQC QC aggregation
- BWA MEM alignment to a 3-genome *E. coli* reference library
- pandas tables (CSV)
- MySQL loading + SQL analysis exports
- matplotlib graphs

Key outputs:
- data/results/tables/final_report.csv
- data/results/sql_outputs/*.csv
- data/results/graphs/*.png

Run:
1) source venv/bin/activate
2) python scripts/app.py
