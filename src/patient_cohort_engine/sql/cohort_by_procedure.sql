-- Patients who had a procedure, by name. $procedure_terms is a comma-separated
-- list of terms matched case-insensitively anywhere in the procedure chunk.
SELECT subject_id,
       list(lower(chunk) ORDER BY lower(chunk)) AS procedures
FROM (
    SELECT DISTINCT subject_id, lower(chunk) AS chunk
    FROM clinical_entities
    WHERE ner_label = 'Procedure'
      AND chunk <> ''
      AND EXISTS (
          SELECT 1
          FROM (SELECT unnest(string_split($procedure_terms, ',')) AS term)
          WHERE term <> ''
            AND lower(chunk) LIKE '%' || lower(term) || '%'
      )
)
GROUP BY subject_id
ORDER BY subject_id
