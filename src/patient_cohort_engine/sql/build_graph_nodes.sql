-- Nodes of the clinical knowledge graph (graph tables, draft 0).
-- node_id = node_type || ':' || key, stable across runs. key is the natural key:
-- the subject id, the RxNorm code with its code system ("rxnorm:11289"), or the
-- lower-cased resolved drug name or finding text.
WITH mentions AS (
    SELECT 'Patient' AS node_type,
           subject_id AS key,
           subject_id AS label,
           json_object('gender', max(gender), 'date_of_birth', CAST(max(date_of_birth) AS VARCHAR))
               ::VARCHAR AS properties
    FROM notes
    GROUP BY subject_id

    UNION ALL BY NAME

    SELECT DISTINCT
           'RxNorm' AS node_type,
           'rxnorm:' || rxnorm_code AS key,
           rxnorm_code AS label,
           NULL::VARCHAR AS properties
    FROM posology
    WHERE rxnorm_code IS NOT NULL AND rxnorm_code <> ''

    UNION ALL BY NAME

    SELECT DISTINCT
           'Drug' AS node_type,
           lower(trim(drug_resolution)) AS key,
           lower(trim(drug_resolution)) AS label,
           NULL::VARCHAR AS properties
    FROM posology
    WHERE drug_resolution IS NOT NULL AND drug_resolution <> ''

    UNION ALL BY NAME

    SELECT ner_label AS node_type,
           lower(trim(chunk)) AS key,
           min(trim(chunk)) AS label,
           NULL::VARCHAR AS properties
    FROM clinical_entities
    WHERE chunk IS NOT NULL AND trim(chunk) <> ''
    GROUP BY ner_label, lower(trim(chunk))
)
SELECT node_type || ':' || key AS node_id,
       node_type,
       key,
       min(label) AS label,
       max(properties) AS properties
FROM mentions
GROUP BY node_type, key
ORDER BY node_id
