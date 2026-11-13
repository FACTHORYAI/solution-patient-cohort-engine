# Sample data

Every file below is synthetic, generated for this repository from hand-written
clinical-note texts; no real patient data. Licence: CC0-1.0. The folder is a few
kilobytes in total, far under the 5 MB per file and 20 MB per folder limits.

| File | What it is | Where it came from | Licence | Synthetic |
| --- | --- | --- | --- | --- |
| `notes.parquet` | 6 clinical notes: subject_id, event_date, text, gender, date_of_birth | Hand-written for this repository | CC0-1.0 | yes |
| `posology.parquet` | Drug-usage relations (dose, frequency) per note, with RxNorm codes and resolved drug names | Hand-written to match `notes.parquet` | CC0-1.0 | yes |
| `clinical_entities.parquet` | Symptoms, procedures, tests and conditions extracted per note | Hand-written to match `notes.parquet` | CC0-1.0 | yes |
| `graph_nodes.parquet` | Knowledge-graph nodes (Patient, Drug, RxNorm, NER, Symptom, Body_Part, Procedure, Test, Disease_Syndrome_Disorder) | Derived from the three tables above by the `build_knowledge_graph` SQL | CC0-1.0 | yes |
| `graph_edges.parquet` | Knowledge-graph edges: patient→rxnorm→drug→chunk chains and patient→finding edges, per date | Derived from the three tables above by the `build_knowledge_graph` SQL | CC0-1.0 | yes |

The RxNorm codes in `posology.parquet` are illustrative identifiers for the sample
(aspirin 1191, warfarin 11289, furosemide 4603 are public RxNorm codes; the rest are
not verified against a vocabulary). A production run resolves codes against a real
drug vocabulary behind the text model.
