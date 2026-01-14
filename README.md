# Sample Alignment Project (WGS QC + Strain Matching)

Automated pipeline for paired-end FASTQ samples:
- replicate subsampling
- FastQC QC aggregation
- BWA MEM alignment to a 3-genome E. coli reference library
- pandas tables (CSV)
- MySQL loading + SQL analysis exports
- matplotlib graphs

Key outputs:
- data/results/tables/final_report.csv
- data/results/graphs/
- data/results/sql_outputs/
