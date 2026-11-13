<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/FACTHORYAI/.github/main/brand/word-mark-only-mono.svg">
    <img alt="Facthory" src="https://raw.githubusercontent.com/FACTHORYAI/.github/main/brand/word-mark-only.svg" width="360">
  </picture>
</p>

# Patient Cohort Engine

Build and compare patient cohorts from records and clinical notes, with inclusion and exclusion criteria, as tables in Facthory.

![Licence: Apache-2.0](https://img.shields.io/badge/licence-Apache--2.0-blue) ![Runs on Facthory](https://img.shields.io/badge/runs%20on-Facthory-1f6feb) ![Status: install coming](https://img.shields.io/badge/status-install%20coming-lightgrey)

> **Install coming.** This is a Facthory solution: its data, analysis code, agent skill and starting pages load into a Facthory workspace as a ready project. Installing from this page is not available yet; this repository is being prepared for it.

## What it does

Patient Cohort Engine turns free-text clinical notes into a patient knowledge graph and answers cohort questions on it, as tables.

1. **Extract.** Two jobs read each note through a text model and return structured rows: drug usage (drug, dose, frequency, RxNorm code) and clinical entities (symptoms, procedures, tests, body parts, conditions). Answers that fail validation go to `rejected_*` tables with the reason.
2. **Build the graph.** One SQL job turns the extracted rows into two tables, `graph_nodes` and `graph_edges`: patient, RxNorm code, drug, and the drug's strength and frequency, plus the patient's symptoms, procedures, tests and conditions. Every edge belongs to one patient on one date.
3. **Ask cohort questions.** Six SQL jobs return the patients that match, with the evidence rows behind each match:
   - who is prescribed a drug, optionally within a date window;
   - who takes a drug at or above a dose;
   - who takes a drug together with another drug from an interacting family (for example warfarin with an NSAID);
   - who had a named procedure;
   - who had several named symptoms on the same day;
   - who has a condition and a named symptom on the same day.

Step 1 needs a text model. Steps 2 and 3 are plain SQL on DuckDB and need none.

## How it works in Facthory

- Jobs read tables and write tables. They draw no screens and own no storage; querying, charting, joining with your own data, permissions and audit belong to the platform.
- The knowledge graph is two tables, not a graph database. Nodes are `(node_type, name)`; edges are `(source, relationship, target)` per patient and date. Any graph view can be drawn from these tables.
- The agent skill in `skills/` and the starter page in `pages/` describe how to work with the tables and the jobs.
- Sample data in this repository is synthetic. No real patient data.

## The design in two pictures

These diagrams show the concept. The workflow diagram is wider than this repository: the jobs here cover the extraction, graph and cohort steps, not the whole platform.

**Workflow.** Unstructured medical sources are prepared, entities and relationships are extracted from them, the curated data is held in a catalog, a knowledge graph is built from it, and the result is a report: a patient journey and a cohort overview.

![Medical knowledge graph workflow: source storage (medical literature, patient records, search logs, product labels, social media, FDA's FAERS database) flows through data curation, NLP engine, data catalog and graph engine to a medical report with patient journey and cohort overview.](docs/images/knowledge-graph-workflow.png)

**Graph schema.** The patient is the hub. Each patient connects to clinical entities (disease, syndrome or disorder; symptom; body part; test; procedure) and to a medication path: patient, RxNorm code, drug, and the extracted details of the drug (route, form, strength, frequency, dosage, duration).

![Patient knowledge graph schema: a Patient hub node linked by IS_DSD, IS_SYMPTOM, IS_BODYPART, IS_TEST and IS_PROCEDURE to clinical entities, and by RXNORM_CODE to an RxNorm node, then DRUG_GENERIC to a Drug node, then DRUG, ROUTE, FORM, STRENGTH, FREQUENCY, DOSAGE and DURATION to an extracted-entity (NER) node.](docs/images/patient-graph-schema.png)

In this repository the knowledge graph is kept as tables: one table of nodes and one of relations (edges), produced by jobs. It is not a graph database.

## Jobs

| Job | What it does | Inputs | Outputs |
| --- | --- | --- | --- |
| `extract_posology` | Extracts drug-usage relations (dose, frequency and more) with RxNorm codes from notes | `notes` | `posology`, `rejected_posology` |
| `extract_entities` | Extracts symptoms, procedures, tests, body parts and conditions from notes | `notes` | `clinical_entities`, `rejected_entities` |
| `build_knowledge_graph` | Builds the clinical knowledge graph as node and edge tables | `notes`, `posology`, `clinical_entities` | `graph_nodes`, `graph_edges` |
| `cohort_by_drug` | Patients prescribed a drug, optionally within a date window | `graph_edges` | `cohort` |
| `cohort_drug_strength` | Patients whose drug has a strength relation at or above a dose in mg | `graph_edges` | `cohort` |
| `cohort_drug_interaction` | Patients on a primary drug who also take one of a family of interacting drugs | `graph_edges` | `cohort` |
| `cohort_by_procedure` | Patients who had a named procedure | `clinical_entities` | `cohort` |
| `cohort_by_symptoms` | Patients with several named symptoms on the same date | `clinical_entities` | `cohort` |
| `cohort_by_condition` | Patients with a condition and a named symptom on the same date | `clinical_entities` | `cohort` |

The two extraction jobs take a `TextModel` (see `src/patient_cohort_engine/text/interface.py`) as a third argument; Facthory provides model access. Named measures live in `metrics/`.

## Data

The sample tables in `data/sample/` are synthetic and CC0-1.0: `notes`, `posology`, `clinical_entities`, `graph_nodes` and `graph_edges`. They are small (6 notes, 6 patients). See [data/README.md](data/README.md) for origin and licence per file. No real patient data.

## Run it locally

```
uv sync
uv run python -m patient_cohort_engine cohort_drug_strength --drug-name warfarin --min-strength-mg 2
uv run pytest
```

`uv run python -m patient_cohort_engine --help` lists every job; each job has its own `--help`. The extraction jobs additionally take `--model-answers <file>` with a recorded-answers JSON (see `tests/recorded_answers.json`), since they need a model behind `text.interface`. Verified on the synthetic sample data only, not yet in a Facthory workspace.

## Open points

- **No clinical text model ships.** `extract_posology` and `extract_entities` run through the `TextModel` interface. The only implementation is `text/recorded.py`, which replays recorded answers for the sample notes. A model must be plugged in behind `text/interface.py` before new notes can be processed. A rules-based stand-in for clinical extraction is deliberately not provided.
- **RxNorm resolution** happens inside the extraction prompt. There is no vocabulary lookup, and the codes in the sample are illustrative.
- **The graph tables have no node ids and no link back to the source text** (note id or span). Edges identify nodes by type and name only.
- **No graph algorithms** are included. Paths, similarity and communities would be added as jobs over the edge tables.
- **Installing into Facthory is not available yet.** The code is verified on the sample data on a laptop only.
- **The sample is small.** Six notes show the shape of the tables, not realistic volumes.
- **The Dockerfile has not been built or verified.**
- **DuckDB 2.x only.** The code uses the DuckDB 2.0 Arrow API (`to_arrow_table`).
- No orchestrator or DAG files: Facthory, or a scheduler, calls the jobs.

## Not for clinical use

This is software for research and analytics. It is not a medical device and must not be used to diagnose or treat a patient. Results can be wrong; a qualified person reviews them.

## Disclaimers

Bandpey GmbH (“Facthory”) does not dispense medical, diagnosis, or treatment advice. This Solution (“tool”) is for informational purposes only and may not be used as a substitute for professional medical advice, treatment, or diagnosis. This tool may not be used within Facthory to process Protected Health Information (“PHI”) as defined in the Health Insurance Portability and Accountability Act of 1996, unless you have executed with Facthory a contract that allows for processing PHI, an accompanying Business Associate Agreement (BAA), and are running this tool within a HIPAA Account.

## Licence

Apache-2.0. See [LICENSE](LICENSE). "Facthory" and the Facthory logo are trademarks of their owner and are not covered by that licence. This includes the logo shown in the diagrams under `docs/images/`.
