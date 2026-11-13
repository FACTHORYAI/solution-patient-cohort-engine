-- Patients whose drug has a STRENGTH fact at or above a dose in mg.
-- $drug_name matches the drug name; the strength value must start with a number
-- ("2 mg", "5 mg"). The patient is the Patient node's key.
SELECT DISTINCT
    patient.key AS subject_id,
    rx.valid_from AS event_date,
    drug.label AS drug_name,
    rxnorm.label AS rxnorm_code,
    strength.value AS strength
FROM graph_edges AS rx
JOIN graph_nodes AS patient
    ON patient.node_id = rx.source_id AND patient.node_type = 'Patient'
JOIN graph_nodes AS rxnorm ON rxnorm.node_id = rx.target_id
JOIN graph_edges AS dg
    ON dg.source_id = rx.target_id
   AND dg.relationship = 'DRUG_GENERIC'
   AND dg.evidence_document_id = rx.evidence_document_id
JOIN graph_nodes AS drug ON drug.node_id = dg.target_id
JOIN graph_edges AS strength
    ON strength.source_id = dg.target_id
   AND strength.relationship = 'STRENGTH'
   AND strength.evidence_document_id = rx.evidence_document_id
WHERE rx.relationship = 'RXNORM_CODE'
  AND lower(drug.label) LIKE '%' || lower($drug_name) || '%'
  AND TRY_CAST(regexp_extract(strength.value, '([0-9]+([.][0-9]+)?)', 1) AS DOUBLE)
      >= $min_strength_mg
ORDER BY subject_id, event_date, drug_name, strength
