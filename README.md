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

Build and compare patient cohorts from records and clinical notes, with inclusion and exclusion criteria, as tables in Facthory.

## How it will work in Facthory

- You install it into a workspace and get a project: sample data, the analysis, the agent's instructions and starting pages.
- Its results are tables and pages in your workspace, so you can query them, chart them and ask the agent about them, inside your permissions.
- Sample data in this repository is synthetic or openly licensed. No real patient data.

## The design in two pictures

These diagrams show the intended design, taken from the original project. They are a concept, not a description of code that already runs here.

**Workflow.** Unstructured medical sources are prepared, entities and relationships are extracted from them, the curated data is held in a catalog, a knowledge graph is built from it, and the result is a report: a patient journey and a cohort overview.

![Medical knowledge graph workflow: source storage (medical literature, patient records, search logs, product labels, social media, FDA's FAERS database) flows through data curation, NLP engine, data catalog and graph engine to a medical report with patient journey and cohort overview.](docs/images/knowledge-graph-workflow.png)

**Graph schema.** The patient is the hub. Each patient connects to clinical entities (disease, syndrome or disorder; symptom; body part; test; procedure) and to a medication path: patient, RxNorm code, drug, and the extracted details of the drug (route, form, strength, frequency, dosage, duration).

![Patient knowledge graph schema: a Patient hub node linked by IS_DSD, IS_SYMPTOM, IS_BODYPART, IS_TEST and IS_PROCEDURE to clinical entities, and by RXNORM_CODE to an RxNorm node, then DRUG_GENERIC to a Drug node, then DRUG, ROUTE, FORM, STRENGTH, FREQUENCY, DOSAGE and DURATION to an extracted-entity (NER) node.](docs/images/patient-graph-schema.png)

In this repository the knowledge graph is kept as tables: one table of nodes and one of relations (edges), produced by jobs. It is not a graph database.

## Not for clinical use

This is software for research and analytics. It is not a medical device and must not be used to diagnose or treat a patient. Results can be wrong; a qualified person reviews them.

## Disclaimers

Bandpey GmbH (“Facthory”) does not dispense medical, diagnosis, or treatment advice. This Solution (“tool”) is for informational purposes only and may not be used as a substitute for professional medical advice, treatment, or diagnosis. This tool may not be used within Facthory to process Protected Health Information (“PHI”) as defined in the Health Insurance Portability and Accountability Act of 1996, unless you have executed with Facthory a contract that allows for processing PHI, an accompanying Business Associate Agreement (BAA), and are running this tool within a HIPAA Account.

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

The sample tables in `data/sample/` are synthetic and openly licensed (CC0-1.0): `notes`, `posology`, `clinical_entities`, `graph_nodes` and `graph_edges`. See [data/README.md](data/README.md) for one row per file with origin and licence. No real patient data.

## Run it locally

```
uv sync
uv run python -m patient_cohort_engine cohort_drug_strength --drug-name warfarin --min-strength-mg 2
uv run pytest
```

`uv run python -m patient_cohort_engine --help` lists every job; each job has its own `--help`. The extraction jobs additionally take `--model-answers <file>` with a recorded-answers JSON (see `tests/recorded_answers.json`), since they need a model behind `text.interface`. Verified on the synthetic sample data only; restructured, not yet verified end to end in a workspace.

## What changed from the original

- Databricks notebooks and Spark DataFrames became a Python 3.12 package: PyArrow tables in and out, joins and aggregations in DuckDB SQL (`sql/`), one job per module.
- The bronze/silver/gold Delta layers became named tables read and written through `io.py`; sample tables are Parquet in `data/sample/`.
- Spark NLP for Healthcare (proprietary: `ner_posology`, `posology_re`, `ner_jsl_slim`, `sbiobertresolve_rxnorm_augmented`) became the `TextModel` interface in `text/`, with prompts in `text/prompts/` and a recorded stand-in for tests; no clinical model is bundled.
- The Neo4j graph database became node and edge tables in DuckDB; the manual Neo4j Browser queries became parameterised cohort jobs.
- `dbutils`, widgets and notebook cells became `Params` dataclasses, an argparse CLI (`python -m patient_cohort_engine <job>`) and plain functions.
- Plots and graph visualisations are not ported; jobs return the tables beneath them.

## Open points

- The restructured code is now in this repository; the two diagrams above remain the design, and the list below says which parts exist and which do not.
- Installing into Facthory is not available yet.
- The proprietary clinical NLP is not replaced: `extract_posology` and `extract_entities` run through the `TextModel` interface, and the only shipped implementation is `text/recorded.py`, which replays recorded answers for tests and demos. A rules-based stand-in for clinical NER would be dishonest, so none is shipped; Facthory must plug a real model in behind `text.interface`.
- RxNorm resolution is folded into the extraction prompt; a real resolver or vocabulary service is not ported.
- The Neo4j graph database, its APOC procedures and the Graph Data Science library are not ported; the graph is node and edge tables only, and no graph algorithms (for example NetworkX) are wired up yet.
- The original's 965-record `data.csv` from the John Snow Labs workshop repository was not republished: its licence was not verified. This repository ships its own smaller synthetic sample instead.
- Byte offsets of the original extraction outputs (`entity1_begin`/`entity1_end`, `begin`/`end`) and the `rx_text` intermediate column are not ported; nothing downstream used them.
- The original's future-dated synthetic records (2060-2125) are represented with dates 2060-2065 in the sample.
- No orchestrator or DAG files: Facthory (or a later scheduler) runs the jobs.
- The Dockerfile follows the template but the image has not been built or verified here.
- `duckdb>=2.0`'s Arrow API moved (`to_arrow_table` replaces `fetch_arrow_table`); the code targets DuckDB 2.0 exactly.

## Licence

Apache-2.0. See [LICENSE](LICENSE). "Facthory" and the Facthory logo are trademarks of their owner and are not covered by that licence. This includes the logo shown in the diagrams under `docs/images/`.
