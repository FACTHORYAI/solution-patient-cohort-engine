-- Patients who had at least $min_symptoms of the named symptoms on the same date.
-- $symptom_terms is a comma-separated list of terms matched case-insensitively
-- anywhere in the symptom chunk.
WITH matched AS (
    SELECT DISTINCT subject_id, event_date, lower(chunk) AS symptom
    FROM clinical_entities
    WHERE ner_label = 'Symptom'
      AND chunk <> ''
      AND EXISTS (
          SELECT 1
          FROM (SELECT unnest(string_split($symptom_terms, ',')) AS term)
          WHERE term <> ''
            AND lower(chunk) LIKE '%' || lower(term) || '%'
      )
),
grouped AS (
    SELECT subject_id,
           event_date,
           list(symptom ORDER BY symptom) AS symptoms,
           count(*) AS num_symptoms
    FROM matched
    GROUP BY subject_id, event_date
)
SELECT subject_id, event_date, symptoms
FROM grouped
WHERE num_symptoms >= $min_symptoms
ORDER BY subject_id, event_date
