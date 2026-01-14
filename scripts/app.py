import subprocess

def sh(cmd):
    print(">>", cmd)
    subprocess.run(cmd, shell=True, check=True)

def main():
    # 1) Run bioinformatics + pandas table creation
    sh("python scripts/run_pipeline.py")

    # 2) Load tables into MySQL
    sh('python scripts/07_load_tables_to_mysql.py --user rnaapp --password "rnaapp_pw123!"')

    # 3) Export SQL analysis outputs
    sh('python scripts/08_export_sql_outputs.py --user rnaapp --password "rnaapp_pw123!"')

    # 4) Generate matplotlib figures
    sh("python scripts/09_make_graphs.py")

    print("\nDONE.")
    print("Key outputs:")
    print(" - data/results/tables/final_report.csv")
    print(" - data/results/sql_outputs/*.csv")

if __name__ == "__main__":
    main()
