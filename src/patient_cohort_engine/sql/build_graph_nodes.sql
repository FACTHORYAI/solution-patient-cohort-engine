-- Nodes of the clinical knowledge graph: patients, drugs, RxNorm codes, NER chunks
-- from the posology relations, and the clinical entities. One row per (node_type, name).
WITH raw_nodes AS (
    SELECT 'Patient' AS node_type,
           subject_id AS name,
           gender,
           CAST(date_of_birth AS DATE) AS date_of_birth
    FROM notes
    GROUP BY subject_id, gender, date_of_birth

    UNION ALL BY NAME

    SELECT 'RxNorm' AS node_type,
           rxnorm_code AS name,
           NULL::VARCHAR AS gender,
           NULL::DATE AS date_of_birth
    FROM posology
    WHERE rxnorm_code IS NOT NULL AND rxnorm_code <> ''
    GROUP BY rxnorm_code

    UNION ALL BY NAME

    SELECT 'Drug' AS node_type,
           drug_resolution AS name,
           NULL::VARCHAR AS gender,
           NULL::DATE AS date_of_birth
    FROM posology
    WHERE drug_resolution IS NOT NULL AND drug_resolution <> ''
    GROUP BY drug_resolution

    UNION ALL BY NAME

    SELECT 'NER' AS node_type,
           chunk1 AS name,
           NULL::VARCHAR AS gender,
           NULL::DATE AS date_of_birth
    FROM posology
    WHERE chunk1 IS NOT NULL AND chunk1 <> ''
    GROUP BY chunk1

    UNION ALL BY NAME

    SELECT 'NER' AS node_type,
           chunk2 AS name,
           NULL::VARCHAR AS gender,
           NULL::DATE AS date_of_birth
    FROM posology
    WHERE chunk2 IS NOT NULL AND chunk2 <> ''
    GROUP BY chunk2

    UNION ALL BY NAME

    SELECT CASE ner_label
               WHEN 'Symptom' THEN 'Symptom'
               WHEN 'Body_Part' THEN 'Body_Part'
               WHEN 'Procedure' THEN 'Procedure'
               WHEN 'Test' THEN 'Test'
               WHEN 'Disease_Syndrome_Disorder' THEN 'Disease_Syndrome_Disorder'
               ELSE ner_label
           END AS node_type,
           chunk AS name,
           NULL::VARCHAR AS gender,
           NULL::DATE AS date_of_birth
    FROM clinical_entities
    WHERE chunk IS NOT NULL AND chunk <> ''
)
SELECT node_type,
       name,
       max(gender) AS gender,
       max(date_of_birth) AS date_of_birth
FROM raw_nodes
GROUP BY node_type, name
ORDER BY node_type, name
