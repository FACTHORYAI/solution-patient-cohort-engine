-- Edges of the clinical knowledge graph (graph tables, draft 0): one fact per row.
--   Patient -RXNORM_CODE-> RxNorm -DRUG_GENERIC-> Drug -<STRENGTH|FREQUENCY|...>-> literal value
--   Patient -IS_SYMPTOM | IS_DSD | IS_TEST | IS_PROCEDURE | IS_BODYPART-> finding
-- Every fact carries the note it came from and, when the text is found in the note,
-- the character span (evidence_start inclusive, evidence_end exclusive, 0-based).
-- valid_from is the note date; valid_to is unknown (null).
WITH pos AS (
    SELECT p.note_id,
           p.subject_id,
           p.event_date,
           p.chunk1,
           p.entity2 AS relationship,
           p.chunk2,
           p.confidence,
           p.rxnorm_code,
           lower(trim(p.drug_resolution)) AS drug_key,
           instr(n.text, p.chunk1) - 1 AS start1,
           -- the detail (strength, frequency, ...) is searched from the drug mention onwards,
           -- so two drugs with the same strength get their own spans
           CASE
               WHEN instr(n.text, p.chunk1) > 0
                    AND instr(substr(n.text, instr(n.text, p.chunk1)), p.chunk2) > 0
               THEN instr(n.text, p.chunk1) - 1
                    + instr(substr(n.text, instr(n.text, p.chunk1)), p.chunk2) - 1
               ELSE instr(n.text, p.chunk2) - 1
           END AS start2
    FROM posology AS p
    LEFT JOIN notes AS n ON n.note_id = p.note_id
),
facts AS (
    SELECT 'Patient:' || subject_id AS source_id,
           'RxNorm:rxnorm:' || rxnorm_code AS target_id,
           'RXNORM_CODE' AS relationship,
           NULL::VARCHAR AS value,
           event_date AS valid_from,
           note_id AS evidence_document_id,
           CASE WHEN start1 >= 0 THEN start1 END AS evidence_start,
           CASE WHEN start1 >= 0 THEN start1 + length(chunk1) END AS evidence_end,
           confidence
    FROM pos
    WHERE rxnorm_code IS NOT NULL AND rxnorm_code <> ''

    UNION ALL

    SELECT 'RxNorm:rxnorm:' || rxnorm_code,
           'Drug:' || drug_key,
           'DRUG_GENERIC',
           NULL::VARCHAR,
           event_date,
           note_id,
           CASE WHEN start1 >= 0 THEN start1 END,
           CASE WHEN start1 >= 0 THEN start1 + length(chunk1) END,
           confidence
    FROM pos
    WHERE rxnorm_code IS NOT NULL AND rxnorm_code <> '' AND drug_key <> ''

    UNION ALL

    SELECT 'Drug:' || drug_key,
           NULL::VARCHAR,
           upper(relationship),
           chunk2,
           event_date,
           note_id,
           CASE WHEN start2 >= 0 THEN start2 END,
           CASE WHEN start2 >= 0 THEN start2 + length(chunk2) END,
           confidence
    FROM pos
    WHERE drug_key <> '' AND relationship <> '' AND chunk2 <> ''

    UNION ALL

    SELECT 'Patient:' || e.subject_id,
           e.ner_label || ':' || lower(trim(e.chunk)),
           CASE e.ner_label
               WHEN 'Symptom' THEN 'IS_SYMPTOM'
               WHEN 'Disease_Syndrome_Disorder' THEN 'IS_DSD'
               WHEN 'Test' THEN 'IS_TEST'
               WHEN 'Procedure' THEN 'IS_PROCEDURE'
               WHEN 'Body_Part' THEN 'IS_BODYPART'
               ELSE 'IS_' || upper(e.ner_label)
           END,
           NULL::VARCHAR,
           e.event_date,
           e.note_id,
           CASE WHEN instr(n.text, e.chunk) > 0 THEN instr(n.text, e.chunk) - 1 END,
           CASE WHEN instr(n.text, e.chunk) > 0
                THEN instr(n.text, e.chunk) - 1 + length(e.chunk) END,
           NULL::DOUBLE
    FROM clinical_entities AS e
    LEFT JOIN notes AS n ON n.note_id = e.note_id
    WHERE e.chunk IS NOT NULL AND trim(e.chunk) <> ''
),
keyed AS (
    SELECT md5(concat_ws('|', source_id, relationship, coalesce(target_id, ''),
                         coalesce(value, ''), evidence_document_id,
                         coalesce(evidence_start, -1))) AS edge_id,
           *
    FROM facts
)
SELECT edge_id,
       any_value(source_id) AS source_id,
       any_value(target_id) AS target_id,
       any_value(relationship) AS relationship,
       any_value(value) AS value,
       any_value(valid_from) AS valid_from,
       NULL::DATE AS valid_to,
       any_value(evidence_document_id) AS evidence_document_id,
       any_value(evidence_start) AS evidence_start,
       any_value(evidence_end) AS evidence_end,
       max(confidence) AS confidence,
       NULL::VARCHAR AS properties
FROM keyed
GROUP BY edge_id
ORDER BY evidence_document_id, source_id, relationship, target_id, value, evidence_start
