-- Patients who take a primary drug together with one of a family of interacting
-- drugs. $primary_drug matches anywhere in the drug name; $interacting_terms is a
-- comma-separated list of terms matched the same way.
WITH drug_use AS (
    SELECT subject_id, event_date, source_name AS drug_name
    FROM graph_edges
    WHERE source_type = 'Drug'
      AND relationship <> 'DRUG_GENERIC'
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
