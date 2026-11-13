-- Edges of the clinical knowledge graph as a table. Every edge belongs to one
-- patient on one date: patient -> rxnorm -> drug -> chunk, plus the patient's
-- symptoms, procedures, tests, body parts and conditions.
SELECT subject_id,
       event_date,
       'Patient' AS source_type,
       subject_id AS source_name,
       'RXNORM_CODE' AS relationship,
       'RxNorm' AS target_type,
       rxnorm_code AS target_name
FROM posology
WHERE rxnorm_code IS NOT NULL AND rxnorm_code <> ''

UNION ALL BY NAME

SELECT subject_id,
       event_date,
       'RxNorm' AS source_type,
       rxnorm_code AS source_name,
       'DRUG_GENERIC' AS relationship,
       'Drug' AS target_type,
       drug_resolution AS target_name
FROM posology
WHERE rxnorm_code IS NOT NULL AND rxnorm_code <> ''
  AND drug_resolution IS NOT NULL AND drug_resolution <> ''

UNION ALL BY NAME

SELECT subject_id,
       event_date,
       'Drug' AS source_type,
       drug_resolution AS source_name,
       entity1 AS relationship,
       'NER' AS target_type,
       chunk1 AS target_name
FROM posology
WHERE drug_resolution IS NOT NULL AND drug_resolution <> ''
  AND entity1 IS NOT NULL AND entity1 <> ''
  AND chunk1 IS NOT NULL AND chunk1 <> ''

UNION ALL BY NAME

SELECT subject_id,
       event_date,
       'Drug' AS source_type,
       drug_resolution AS source_name,
       entity2 AS relationship,
       'NER' AS target_type,
       chunk2 AS target_name
FROM posology
WHERE drug_resolution IS NOT NULL AND drug_resolution <> ''
  AND entity2 IS NOT NULL AND entity2 <> ''
  AND chunk2 IS NOT NULL AND chunk2 <> ''

UNION ALL BY NAME

SELECT subject_id,
       event_date,
       'Patient' AS source_type,
       subject_id AS source_name,
       'IS_SYMPTOM' AS relationship,
       'Symptom' AS target_type,
       chunk AS target_name
FROM clinical_entities
WHERE ner_label = 'Symptom' AND chunk <> ''

UNION ALL BY NAME

SELECT subject_id,
       event_date,
       'Patient' AS source_type,
       subject_id AS source_name,
       'IS_DSD' AS relationship,
       'Disease_Syndrome_Disorder' AS target_type,
       chunk AS target_name
FROM clinical_entities
WHERE ner_label = 'Disease_Syndrome_Disorder' AND chunk <> ''

UNION ALL BY NAME

SELECT subject_id,
       event_date,
       'Patient' AS source_type,
       subject_id AS source_name,
       'IS_TEST' AS relationship,
       'Test' AS target_type,
       chunk AS target_name
FROM clinical_entities
WHERE ner_label = 'Test' AND chunk <> ''

UNION ALL BY NAME

SELECT subject_id,
       event_date,
       'Patient' AS source_type,
       subject_id AS source_name,
       'IS_BODYPART' AS relationship,
       'Body_Part' AS target_type,
       chunk AS target_name
FROM clinical_entities
WHERE ner_label = 'Body_Part' AND chunk <> ''

UNION ALL BY NAME

SELECT subject_id,
       event_date,
       'Patient' AS source_type,
       subject_id AS source_name,
       'IS_PROCEDURE' AS relationship,
       'Procedure' AS target_type,
       chunk AS target_name
FROM clinical_entities
WHERE ner_label = 'Procedure' AND chunk <> ''
ORDER BY subject_id, event_date, source_type, source_name, relationship, target_type, target_name
