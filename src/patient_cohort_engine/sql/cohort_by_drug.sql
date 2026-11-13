-- Patients prescribed a drug: Patient -RXNORM_CODE-> RxNorm -DRUG_GENERIC-> Drug, with the
-- drug's literal details (strength, frequency, ...) from the same note. $drug_name matches
-- anywhere in the drug name, case-insensitive; empty $start_date or $end_date means
-- unbounded. The patient is the Patient node's key.
SELECT DISTINCT
    patient.key AS subject_id,
    rx.valid_from AS event_date,
    drug.label AS drug_name,
    rxnorm.label AS rxnorm_code,
    detail.relationship || ' (' || detail.value || ')' AS details
FROM graph_edges AS rx
JOIN graph_nodes AS patient
    ON patient.node_id = rx.source_id AND patient.node_type = 'Patient'
JOIN graph_nodes AS rxnorm ON rxnorm.node_id = rx.target_id
JOIN graph_edges AS dg
    ON dg.source_id = rx.target_id
   AND dg.relationship = 'DRUG_GENERIC'
   AND dg.evidence_document_id = rx.evidence_document_id
JOIN graph_nodes AS drug ON drug.node_id = dg.target_id
JOIN graph_edges AS detail
    ON detail.source_id = dg.target_id
   AND detail.value IS NOT NULL
   AND detail.evidence_document_id = rx.evidence_document_id
WHERE rx.relationship = 'RXNORM_CODE'
  AND lower(drug.label) LIKE '%' || lower($drug_name) || '%'
  AND ($start_date = '' OR rx.valid_from >= TRY_CAST($start_date AS DATE))
  AND ($end_date = '' OR rx.valid_from < TRY_CAST($end_date AS DATE))
ORDER BY subject_id, event_date, drug_name, rxnorm_code, details
