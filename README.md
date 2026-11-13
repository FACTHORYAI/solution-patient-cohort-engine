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

## Open points

- The analysis code is not in this repository yet; it is being restructured from the original project. Until it lands, nothing here runs.
- Installing into Facthory is not available yet.
- The two diagrams above are the design, not a map of finished code. This list will name which parts exist as code and which are still to be written.

## Licence

Apache-2.0. See [LICENSE](LICENSE). "Facthory" and the Facthory logo are trademarks of their owner and are not covered by that licence. This includes the logo shown in the diagrams under `docs/images/`.
