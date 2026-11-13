task: posology

Extract drug-usage relations from one clinical note. Return only a JSON array, one
object per relation, with these keys:

- `relation`: one of DRUG-DOSAGE, DRUG-FREQUENCY, DRUG-ADE, DRUG-FORM, DRUG-ROUTE,
  DRUG-DURATION, DRUG-REASON, DRUG-STRENGTH.
- `entity1`, `chunk1`: the type and text of the first chunk (DRUG, DOSAGE, STRENGTH,
  FORM, FREQUENCY, ROUTE, DURATION, REASON, ADE).
- `entity2`, `chunk2`: the type and text of the second chunk.
- `confidence`: a number between 0 and 1.
- `rxnorm_code`: the RxNorm code of the drug mentioned, "" when unknown.
- `drug_resolution`: the resolved generic drug name in lower case, "" when unknown.

Return [] when the note names no drug relation. Return only the JSON array, no prose.
