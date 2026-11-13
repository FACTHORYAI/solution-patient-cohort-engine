-- Patients prescribed a drug: patient -> rxnorm -> drug -> chunk, optionally within
-- a date window. $drug_name matches anywhere in the resolved drug name, case-insensitive;
-- empty $start_date or $end_date means unbounded.
SELECT DISTINCT
    rx.subject_id,
    rx.event_date,
    drug.target_name AS drug_name,
    rx.target_name AS rxnorm_code,
    ner.relationship || ' (' || ner.target_name || ')' AS details
FROM graph_edges AS rx
JOIN graph_edges AS drug
    ON drug.subject_id = rx.subject_id
   AND drug.event_date = rx.event_date
   AND drug.source_type = 'RxNorm'
   AND drug.source_name = rx.target_name
   AND drug.relationship = 'DRUG_GENERIC'
JOIN graph_edges AS ner
    ON ner.subject_id = rx.subject_id
   AND ner.event_date = rx.event_date
   AND ner.source_type = 'Drug'
   AND ner.source_name = drug.target_name
WHERE rx.source_type = 'Patient'
  AND rx.relationship = 'RXNORM_CODE'
  AND lower(drug.target_name) LIKE '%' || lower($drug_name) || '%'
  AND ($start_date = '' OR rx.event_date >= TRY_CAST($start_date AS DATE))
  AND ($end_date = '' OR rx.event_date < TRY_CAST($end_date AS DATE))
ORDER BY subject_id, event_date, drug_name, rxnorm_code, details
