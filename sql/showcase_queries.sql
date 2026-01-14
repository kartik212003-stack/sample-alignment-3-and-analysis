USE sample_alignment;

-- Q1: Final report (one-row-per-sample decision table)
SELECT * FROM final_report
ORDER BY avg_mapping_rate_all DESC;

-- Q2: Identify NO_MATCH samples (e.g., human negative control)
SELECT sample_id, avg_mapping_rate_all, avg_mapping_rate_mapq30, classification
FROM sample_alignment_summary
WHERE classification='NO_MATCH';

-- Q3: “Best match” ranking by mapping rate (ALL reads)
SELECT sample_id, avg_mapping_rate_all, best_variant, confidence_gap
FROM sample_alignment_summary
ORDER BY avg_mapping_rate_all DESC;

-- Q4: Confidence gap ranking (how decisive is the best variant?)
SELECT sample_id, best_variant, best_mapped_per_mb, second_mapped_per_mb, confidence_gap
FROM sample_alignment_summary
ORDER BY confidence_gap DESC;

-- Q5: Replicate stability: mapping rate range across replicates
SELECT sample_id,
       MIN(mapping_rate) AS min_map,
       MAX(mapping_rate) AS max_map,
       (MAX(mapping_rate) - MIN(mapping_rate)) AS range_map
FROM align_totals
WHERE filter='all'
GROUP BY sample_id
ORDER BY range_map DESC;

-- Q6: Variant competition per sample (MAPQ30)
SELECT sample_id, variant,
       AVG(percent_of_mapped) AS avg_percent_of_mapped,
       AVG(mapped_per_mb) AS avg_mapped_per_mb
FROM align_metrics_by_variant
WHERE filter='mapq30'
GROUP BY sample_id, variant
ORDER BY sample_id, avg_mapped_per_mb DESC;

-- Q7: QC failures per sample (which tests fail)
SELECT sample_id, test, COUNT(*) AS fail_count
FROM qc_metrics
WHERE status='FAIL'
GROUP BY sample_id, test
ORDER BY sample_id, fail_count DESC;

-- Q8: QC vs mapping (basic joined view)
SELECT q.sample_id, q.FAIL, q.qc_fail_rate, a.avg_mapping_rate_all, a.classification
FROM sample_qc_summary q
JOIN sample_alignment_summary a USING(sample_id)
ORDER BY a.avg_mapping_rate_all DESC;
