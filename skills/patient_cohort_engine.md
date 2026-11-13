# Patient Cohort Engine — agent instructions

You help members build and compare patient cohorts from clinical notes in this project.

## What the project provides

- Sample tables in `data/sample`: `notes` (synthetic clinical notes with demographics), `posology` (drug-usage relations with RxNorm codes), `clinical_entities` (symptoms, procedures, tests and conditions per note), and `graph_nodes` / `graph_edges` (the knowledge graph as tables). Every row carries a `note_id`. All synthetic.
- Jobs under `src/patient_cohort_engine/jobs`: two extraction jobs that read notes through a `TextModel` (`text/interface.py`), one job that turns extracted rows into graph node and edge tables, and six cohort queries.

## How to answer a cohort question

1. Classify what the member asks: who is prescribed a drug (`cohort_by_drug`), at what dose (`cohort_drug_strength`), together with which other drug (`cohort_drug_interaction`), who had a procedure (`cohort_by_procedure`), who had several symptoms on the same day (`cohort_by_symptoms`), or a condition plus a symptom (`cohort_by_condition`).
2. Check the parameters with `uv run python -m patient_cohort_engine <job> --help`; drug and term matches are case-insensitive "contains" matches; symptoms and conditions must co-occur on the same date.
3. Run the job, or answer directly from the tables: `graph_nodes` holds one row per node (`node_id`, `node_type`, `key`, `label`); `graph_edges` holds one fact per row: `Patient -RXNORM_CODE-> RxNorm -DRUG_GENERIC-> Drug`, the drug's literal details (`STRENGTH`, `FREQUENCY`, in `value`), and `Patient -IS_SYMPTOM / IS_DSD / IS_TEST / IS_PROCEDURE / IS_BODYPART-> finding`. Join edges to nodes on `source_id` / `target_id`; filter with SQL.
4. Every edge names the note it came from (`evidence_document_id`) and, when found, the character span (`evidence_start`, `evidence_end`) in that note's text. Quote that evidence when you explain a match.
5. Report the cohort as a table with `subject_id` and the evidence columns. Say which rows are matched, never guess beyond the tables.

## Data care

- The sample data is synthetic and openly licensed; real patient data never enters this project.
- The two extraction jobs need a model behind `text.interface`; the repository ships only a recorded stand-in for tests, so do not run them expecting clinical accuracy.
- Results are for research and analytics, not clinical decisions. Say so when a result could be read as medical advice.
