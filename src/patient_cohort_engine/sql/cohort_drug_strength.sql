-- Patients whose drug has a DRUG-STRENGTH relation at or above a dose in mg.
-- $drug_name matches the resolved drug name; the strength chunk must start with
-- a number ("2 mg", "5 mg").
SELECT DISTINCT
    ner.subject_id,
    ner.event_date,
    ner.source_name AS drug_name,
    rx.target_name AS rxnorm_code,
    ner.target_name AS strength
FROM graph_edges AS ner
LEFT JOIN graph_edges AS rx
    ON rx.subject_id = ner.subject_id
   AND rx.event_date = ner.event_date
   AND rx.source_type = 'Patient'
   AND rx.relationship = 'RXNORM_CODE'
   AND rx.target_name IN (
        SELECT dg.target_name
        FROM graph_edges AS dg
        WHERE dg.subject_id = ner.subject_id
          AND dg.event_date = ner.event_date
          AND dg.source_type = 'RxNorm'
          AND dg.relationship = 'DRUG_GENERIC'
          AND lower(dg.target_name) = lower(ner.source_name)
   )
WHERE ner.source_type = 'Drug'
  AND ner.relationship = 'STRENGTH'
  AND lower(ner.source_name) LIKE '%' || lower($drug_name) || '%'
  AND TRY_CAST(regexp_extract(ner.target_name, '([0-9]+([.][0-9]+)?)', 1) AS DOUBLE) >= $min_strength_mg
ORDER BY subject_id, event_date, drug_name, strength
