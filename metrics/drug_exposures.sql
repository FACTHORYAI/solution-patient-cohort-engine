-- How many drug exposures the knowledge graph records: one per patient, note and drug.
SELECT count(DISTINCT source_id || '|' || evidence_document_id || '|' || target_id) AS drug_exposures
FROM graph_edges
WHERE relationship = 'RXNORM_CODE';
