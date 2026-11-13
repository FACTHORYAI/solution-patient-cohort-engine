# Patient Cohort Engine

Build and compare patient cohorts from clinical notes.

## Start here

1. Look at the sample tables in `data/sample` (synthetic): `notes`, `posology`, `clinical_entities`, and the graph tables `graph_nodes` and `graph_edges` they build.
2. Read `graph_edges`: every row is one piece of evidence — `patient -> rxnorm -> drug -> chunk` for prescriptions, `patient -> symptom / procedure / condition` for findings, all tied to a patient and a date.
3. Ask a cohort question and run its job:

| Question | Job |
| --- | --- |
| Who is prescribed a drug, since when? | `cohort_by_drug` |
| Who takes a drug at a dose of 2 mg or more? | `cohort_drug_strength` |
| Who takes warfarin with an NSAID? | `cohort_drug_interaction` |
| Who had a hernia repair, appendectomy or cholecystectomy? | `cohort_by_procedure` |
| Who had chest pain and shortness of breath on the same day? | `cohort_by_symptoms` |
| Who has hypertension or diabetes and chest pain? | `cohort_by_condition` |

## Notes

- The sample data is synthetic; real patient data never enters this project.
- The extraction jobs need a text model behind `patient_cohort_engine.text.interface`; a recorded stand-in exists for tests. Cohort jobs run without any model.
- Results are for research and analytics, not clinical decisions.
