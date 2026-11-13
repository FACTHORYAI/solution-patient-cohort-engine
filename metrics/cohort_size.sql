-- The size of a cohort table.
SELECT count(DISTINCT subject_id) AS cohort_size
FROM cohort;
