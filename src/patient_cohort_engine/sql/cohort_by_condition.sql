-- Patients who had a named symptom on a date they also carried a named condition
-- (disease, syndrome or disorder). $condition_terms and $symptom_term are
-- comma-separated lists of terms matched case-insensitively.
SELECT DISTINCT
    dsd.subject_id,
    dsd.event_date,
    dsd.condition,
    sym.symptom
FROM (
    SELECT subject_id, event_date, lower(chunk) AS condition
    FROM clinical_entities
    WHERE ner_label = 'Disease_Syndrome_Disorder'
      AND chunk <> ''
      AND EXISTS (
          SELECT 1
          FROM (SELECT unnest(string_split($condition_terms, ',')) AS term)
          WHERE term <> ''
            AND lower(chunk) LIKE '%' || lower(term) || '%'
      )
) AS dsd
JOIN (
    SELECT subject_id, event_date, lower(chunk) AS symptom
    FROM clinical_entities
    WHERE ner_label = 'Symptom'
      AND chunk <> ''
      AND EXISTS (
          SELECT 1
          FROM (SELECT unnest(string_split($symptom_term, ',')) AS term)
          WHERE term <> ''
            AND lower(chunk) LIKE '%' || lower(term) || '%'
      )
) AS sym
    ON sym.subject_id = dsd.subject_id
   AND sym.event_date = dsd.event_date
ORDER BY dsd.subject_id, dsd.event_date, dsd.condition, sym.symptom
