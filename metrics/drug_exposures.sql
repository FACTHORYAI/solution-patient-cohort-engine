-- How many drug exposures the knowledge graph records, one per patient and date.
SELECT count(*) AS drug_exposures
FROM graph_edges
WHERE relationship = 'RXNORM_CODE';
