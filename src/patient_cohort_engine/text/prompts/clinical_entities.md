task: clinical_entities

Extract clinical entities from one clinical note. Return only a JSON array, one
object per entity, with these keys:

- `sentence_id`: the 0-based index of the sentence that contains the chunk.
- `chunk`: the entity text.
- `ner_label`: one of Symptom, Body_Part, Procedure, Disease_Syndrome_Disorder, Test.

Return [] when the note contains none. Return only the JSON array, no prose.
