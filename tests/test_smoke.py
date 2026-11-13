"""One smoke test per job, on the synthetic sample data."""

from __future__ import annotations

from pathlib import Path

import pytest

from patient_cohort_engine import io
from patient_cohort_engine.config import Settings
from patient_cohort_engine.jobs import REGISTRY, call_run
from patient_cohort_engine.jobs.build_knowledge_graph import Params as GraphParams
from patient_cohort_engine.jobs.cohort_by_condition import Params as ConditionParams
from patient_cohort_engine.jobs.cohort_by_drug import Params as DrugParams
from patient_cohort_engine.jobs.cohort_by_procedure import Params as ProcedureParams
from patient_cohort_engine.jobs.cohort_by_symptoms import Params as SymptomsParams
from patient_cohort_engine.jobs.cohort_drug_interaction import Params as InteractionParams
from patient_cohort_engine.jobs.cohort_drug_strength import Params as StrengthParams
from patient_cohort_engine.jobs.extract_entities import Params as EntityParams
from patient_cohort_engine.jobs.extract_posology import Params as PosologyParams
from patient_cohort_engine.schemas import (
    CLINICAL_ENTITIES,
    COHORT_CONDITION,
    COHORT_DRUG,
    COHORT_DRUG_INTERACTION,
    COHORT_DRUG_STRENGTH,
    COHORT_PROCEDURE,
    COHORT_SYMPTOMS,
    GRAPH_EDGES,
    GRAPH_NODES,
    POSOLOGY,
)
from patient_cohort_engine.text.recorded import RecordedTextModel, load_answers

REPO = Path(__file__).resolve().parent.parent
SETTINGS = Settings(sample_dir=REPO / "data" / "sample", output_dir=REPO / "output")


@pytest.fixture(scope="module")
def recorded_model() -> RecordedTextModel:
    return RecordedTextModel(load_answers(io.read_json(REPO / "tests" / "recorded_answers.json")))


@pytest.fixture(scope="module")
def tables() -> dict[str, object]:
    return {
        name: io.read_table(name, SETTINGS)
        for name in ("notes", "posology", "clinical_entities", "graph_nodes", "graph_edges")
    }


def run_job(name: str, tables: dict, params, model=None):
    return call_run(REGISTRY[name], tables, params, model)


def graph(tables: dict) -> dict:
    return {name: tables[name] for name in ("graph_nodes", "graph_edges")}


def subjects(cohort) -> set[str]:
    return set(cohort.column("subject_id").to_pylist())


def test_extract_posology(tables: dict, recorded_model: RecordedTextModel) -> None:
    outputs = run_job(
        "extract_posology", {"notes": tables["notes"]}, PosologyParams(), recorded_model
    )
    posology = outputs["posology"]
    assert posology.schema.equals(POSOLOGY)
    assert posology.equals(tables["posology"].select(POSOLOGY.names))
    assert outputs["rejected_posology"].num_rows == 0


def test_extract_entities(tables: dict, recorded_model: RecordedTextModel) -> None:
    outputs = run_job(
        "extract_entities", {"notes": tables["notes"]}, EntityParams(), recorded_model
    )
    entities = outputs["clinical_entities"]
    assert entities.schema.equals(CLINICAL_ENTITIES)
    assert entities.equals(tables["clinical_entities"].select(CLINICAL_ENTITIES.names))
    assert outputs["rejected_entities"].num_rows == 0


def test_build_knowledge_graph(tables: dict) -> None:
    inputs = {name: tables[name] for name in ("notes", "posology", "clinical_entities")}
    outputs = run_job("build_knowledge_graph", inputs, GraphParams())
    assert outputs["graph_nodes"].schema.equals(GRAPH_NODES)
    assert outputs["graph_edges"].schema.equals(GRAPH_EDGES)
    assert outputs["graph_nodes"].equals(tables["graph_nodes"].select(GRAPH_NODES.names))
    assert outputs["graph_edges"].equals(tables["graph_edges"].select(GRAPH_EDGES.names))


def test_graph_tables_follow_the_contract(tables: dict) -> None:
    nodes = tables["graph_nodes"].to_pylist()
    edges = tables["graph_edges"].to_pylist()
    notes = {row["note_id"]: row["text"] for row in tables["notes"].to_pylist()}
    node_ids = {node["node_id"] for node in nodes}
    assert len(node_ids) == len(nodes)
    assert all(node["node_id"] == f"{node['node_type']}:{node['key']}" for node in nodes)
    assert len({edge["edge_id"] for edge in edges}) == len(edges)
    for edge in edges:
        assert edge["source_id"] in node_ids
        # A fact points at a node or holds a literal value, never both.
        assert (edge["target_id"] in node_ids) != (edge["value"] is not None)
        assert edge["evidence_document_id"] in notes
        if edge["evidence_start"] is not None:
            span = notes[edge["evidence_document_id"]][
                edge["evidence_start"] : edge["evidence_end"]
            ]
            assert span.lower() == (edge["value"] or span).lower()


def test_cohort_by_drug(tables: dict) -> None:
    cohort = run_job("cohort_by_drug", graph(tables), DrugParams(drug_name="lasix"))["cohort"]
    assert cohort.schema.equals(COHORT_DRUG)
    assert subjects(cohort) == {"10001"}


def test_cohort_by_drug_date_window(tables: dict) -> None:
    cohort = run_job(
        "cohort_by_drug",
        graph(tables),
        DrugParams(drug_name="isosorbide", start_date="2060-01-01", end_date="2063-01-01"),
    )["cohort"]
    assert subjects(cohort) == {"10003"}


def test_cohort_drug_strength(tables: dict) -> None:
    cohort = run_job(
        "cohort_drug_strength",
        graph(tables),
        StrengthParams(drug_name="warfarin", min_strength_mg=3.0),
    )["cohort"]
    assert cohort.schema.equals(COHORT_DRUG_STRENGTH)
    assert subjects(cohort) == {"10002"}
    assert cohort.column("strength").to_pylist() == ["5 mg"]
    assert cohort.column("rxnorm_code").to_pylist() == ["11289"]


def test_cohort_drug_interaction(tables: dict) -> None:
    cohort = run_job("cohort_drug_interaction", graph(tables), InteractionParams())["cohort"]
    assert cohort.schema.equals(COHORT_DRUG_INTERACTION)
    assert subjects(cohort) == {"10004"}
    assert cohort.column("interacting_drugs").to_pylist() == [["ibuprofen"]]


def test_cohort_by_procedure(tables: dict) -> None:
    cohort = run_job(
        "cohort_by_procedure",
        {"clinical_entities": tables["clinical_entities"]},
        ProcedureParams(procedure_terms="hernia repair,appendectomy,cholecystectomy"),
    )["cohort"]
    assert cohort.schema.equals(COHORT_PROCEDURE)
    assert subjects(cohort) == {"10002", "10004", "10005"}


def test_cohort_by_symptoms(tables: dict) -> None:
    cohort = run_job(
        "cohort_by_symptoms",
        {"clinical_entities": tables["clinical_entities"]},
        SymptomsParams(symptom_terms="chest pain,shortness of breath"),
    )["cohort"]
    assert cohort.schema.equals(COHORT_SYMPTOMS)
    assert subjects(cohort) == {"10001"}


def test_cohort_by_condition(tables: dict) -> None:
    cohort = run_job(
        "cohort_by_condition",
        {"clinical_entities": tables["clinical_entities"]},
        ConditionParams(condition_terms="hypertension,diabetes", symptom_term="chest pain"),
    )["cohort"]
    assert cohort.schema.equals(COHORT_CONDITION)
    assert subjects(cohort) == {"10001", "10003"}
