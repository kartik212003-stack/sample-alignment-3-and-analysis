CREATE DATABASE IF NOT EXISTS sample_alignment;
USE sample_alignment;

DROP TABLE IF EXISTS qc_metrics;
CREATE TABLE qc_metrics (
  sample_id   VARCHAR(50),
  replicate   INT,
  mate        INT,
  test        VARCHAR(200),
  status      VARCHAR(10),
  fastq_file  VARCHAR(255)
);

DROP TABLE IF EXISTS align_totals;
CREATE TABLE align_totals (
  sample_id       VARCHAR(50),
  replicate       INT,
  filter          VARCHAR(20),
  total_reads     INT,
  total_mapped    INT,
  total_unmapped  INT,
  mapping_rate    DOUBLE
);

DROP TABLE IF EXISTS align_metrics_by_variant;
CREATE TABLE align_metrics_by_variant (
  sample_id          VARCHAR(50),
  replicate          INT,
  filter             VARCHAR(20),
  variant            VARCHAR(50),
  length             INT,
  mapped             INT,
  percent_of_mapped  DOUBLE,
  mapped_per_mb      DOUBLE
);

DROP TABLE IF EXISTS sample_qc_summary;
CREATE TABLE sample_qc_summary (
  sample_id     VARCHAR(50) PRIMARY KEY,
  FAIL          INT,
  PASS          INT,
  WARN          INT,
  qc_fail_rate  DOUBLE
);

DROP TABLE IF EXISTS sample_alignment_summary;
CREATE TABLE sample_alignment_summary (
  sample_id               VARCHAR(50) PRIMARY KEY,
  avg_total_reads_all     DOUBLE,
  avg_mapped_all          DOUBLE,
  avg_unmapped_all        DOUBLE,
  avg_mapping_rate_all    DOUBLE,
  avg_mapped_mapq30       DOUBLE,
  avg_mapping_rate_mapq30 DOUBLE,
  best_variant            VARCHAR(50),
  best_mapped_per_mb      DOUBLE,
  second_mapped_per_mb    DOUBLE,
  confidence_gap          DOUBLE,
  classification          VARCHAR(20)
);

DROP TABLE IF EXISTS final_report;
CREATE TABLE final_report (
  sample_id               VARCHAR(50) PRIMARY KEY,
  FAIL                    INT,
  PASS                    INT,
  WARN                    INT,
  qc_fail_rate            DOUBLE,
  avg_total_reads_all     DOUBLE,
  avg_mapped_all          DOUBLE,
  avg_unmapped_all        DOUBLE,
  avg_mapping_rate_all    DOUBLE,
  avg_mapped_mapq30       DOUBLE,
  avg_mapping_rate_mapq30 DOUBLE,
  best_variant            VARCHAR(50),
  best_mapped_per_mb      DOUBLE,
  second_mapped_per_mb    DOUBLE,
  confidence_gap          DOUBLE,
  classification          VARCHAR(20)
);
