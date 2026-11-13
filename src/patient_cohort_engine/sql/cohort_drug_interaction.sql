-- Patients who take a primary drug together with one of a family of interacting
-- drugs. $primary_drug matches anywhere in the drug name; $interacting_terms is a
-- comma-separated list of terms matched the same way.
WITH drug_use AS (
    SELECT patient.key AS subject_id,
           rx.valid_from AS event_date,
           drug.label AS drug_name
    FROM graph_edges AS rx
    JOIN graph_nodes AS patient
        ON patient.node_id = rx.source_id AND patient.node_type = 'Patient'
    JOIN graph_edges AS dg
        ON dg.source_id = rx.target_id
       AND dg.relationship = 'DRUG_GENERIC'
       AND dg.evidence_document_id = rx.evidence_document_id
    JOIN graph_nodes AS drug ON drug.node_id = dg.target_id
    WHERE rx.relationship = 'RXNORM_CODE'
),
interacting AS (
    SELECT subject_id,
           list(lower(drug_name) ORDER BY lower(drug_name)) AS interacting_drugs
    FROM (
        SELECT DISTINCT subject_id, lower(drug_name) AS drug_name
        FROM drug_use
        WHERE EXISTS (
            SELECT 1
            FROM (SELECT unnest(string_split($interacting_terms, ',')) AS term)
            WHERE term <> ''
              AND lower(drug_name) LIKE '%' || lower(term) || '%'
        )
    )
    GROUP BY subject_id
),
primary_use AS (
    SELECT DISTINCT subject_id, event_date, drug_name AS primary_drug
    FROM drug_use
    WHERE lower(drug_name) LIKE '%' || lower($primary_drug) || '%'
)
SELECT pu.subject_id,
       pu.event_date,
       pu.primary_drug,
       inn.interacting_drugs
FROM primary_use AS pu
JOIN interacting AS inn ON inn.subject_id = pu.subject_id
ORDER BY pu.subject_id, pu.event_date, pu.primary_drug
