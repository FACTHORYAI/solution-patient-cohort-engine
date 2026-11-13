"""The jobs of this solution: plain functions from named tables to named tables."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import pyarrow as pa

from patient_cohort_engine.jobs import (
    build_knowledge_graph,
    cohort_by_condition,
    cohort_by_drug,
    cohort_by_procedure,
    cohort_by_symptoms,
    cohort_drug_interaction,
    cohort_drug_strength,
    extract_entities,
    extract_posology,
)


@dataclass(frozen=True)
class JobSpec:
    """One job: its callable, its parameter class and its input and output tables."""

    name: str
    description: str
    run: Callable[..., dict[str, pa.Table]]
    params_cls: type
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    needs_model: bool = False


REGISTRY: dict[str, JobSpec] = {
    spec.name: spec
    for spec in (
        JobSpec(
            name="extract_posology",
            description="Extract drug-usage relations with RxNorm codes from clinical notes.",
            run=extract_posology.run,
            params_cls=extract_posology.Params,
            inputs=extract_posology.INPUTS,
            outputs=extract_posology.OUTPUTS,
            needs_model=True,
        ),
        JobSpec(
            name="extract_entities",
            description="Extract clinical entities (symptoms, procedures, tests) from notes.",
            run=extract_entities.run,
            params_cls=extract_entities.Params,
            inputs=extract_entities.INPUTS,
            outputs=extract_entities.OUTPUTS,
            needs_model=True,
        ),
        JobSpec(
            name="build_knowledge_graph",
            description="Build the clinical knowledge graph as node and edge tables.",
            run=build_knowledge_graph.run,
            params_cls=build_knowledge_graph.Params,
            inputs=build_knowledge_graph.INPUTS,
            outputs=build_knowledge_graph.OUTPUTS,
        ),
        JobSpec(
            name="cohort_by_drug",
            description="Patients prescribed a drug, optionally within a date window.",
            run=cohort_by_drug.run,
            params_cls=cohort_by_drug.Params,
            inputs=cohort_by_drug.INPUTS,
            outputs=cohort_by_drug.OUTPUTS,
        ),
        JobSpec(
            name="cohort_drug_strength",
            description="Patients whose drug has a strength relation at or above a dose.",
            run=cohort_drug_strength.run,
            params_cls=cohort_drug_strength.Params,
            inputs=cohort_drug_strength.INPUTS,
            outputs=cohort_drug_strength.OUTPUTS,
        ),
        JobSpec(
            name="cohort_drug_interaction",
            description="Patients on a primary drug who also take an interacting drug.",
            run=cohort_drug_interaction.run,
            params_cls=cohort_drug_interaction.Params,
            inputs=cohort_drug_interaction.INPUTS,
            outputs=cohort_drug_interaction.OUTPUTS,
        ),
        JobSpec(
            name="cohort_by_procedure",
            description="Patients who had a named procedure.",
            run=cohort_by_procedure.run,
            params_cls=cohort_by_procedure.Params,
            inputs=cohort_by_procedure.INPUTS,
            outputs=cohort_by_procedure.OUTPUTS,
        ),
        JobSpec(
            name="cohort_by_symptoms",
            description="Patients with several named symptoms on the same date.",
            run=cohort_by_symptoms.run,
            params_cls=cohort_by_symptoms.Params,
            inputs=cohort_by_symptoms.INPUTS,
            outputs=cohort_by_symptoms.OUTPUTS,
        ),
        JobSpec(
            name="cohort_by_condition",
            description="Patients with a condition and a named symptom on the same date.",
            run=cohort_by_condition.run,
            params_cls=cohort_by_condition.Params,
            inputs=cohort_by_condition.INPUTS,
            outputs=cohort_by_condition.OUTPUTS,
        ),
    )
}


def param_values(spec: JobSpec, args: Any) -> Any:
    """Build the job's Params instance from parsed command-line arguments."""
    values = {
        field.name: getattr(args, field.name)
        for field in spec.params_cls.__dataclass_fields__.values()
    }
    return spec.params_cls(**values)


def call_run(
    spec: JobSpec, inputs: dict[str, pa.Table], params: Any, model: Any
) -> dict[str, pa.Table]:
    """Call the job's run with the arguments its signature asks for."""
    if spec.needs_model:
        return spec.run(inputs=inputs, params=params, model=model)
    return spec.run(inputs=inputs, params=params)
