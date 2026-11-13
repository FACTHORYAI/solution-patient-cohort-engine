"""Patients who had several named symptoms on the same date."""

from __future__ import annotations

from dataclasses import dataclass

import pyarrow as pa

from patient_cohort_engine import io
from patient_cohort_engine.jobs._duck import align, run_query
from patient_cohort_engine.schemas import COHORT_SYMPTOMS

INPUTS = ("clinical_entities",)
OUTPUTS = ("cohort",)


@dataclass(frozen=True)
class Params:
    """Parameters for the symptom cohort."""

    symptom_terms: str = ""
    min_symptoms: int = 2


def run(inputs: dict[str, pa.Table], params: Params) -> dict[str, pa.Table]:
    """Return the patients with at least min_symptoms of the named symptoms on one date."""
    if not params.symptom_terms.strip():
        message = "Parameter symptom_terms is empty; cohort_by_symptoms needs terms"
        raise ValueError(message)
    if params.min_symptoms < 1:
        message = "Parameter min_symptoms must be at least 1"
        raise ValueError(message)
    table = run_query(
        io.read_sql("cohort_by_symptoms"),
        inputs,
        {"symptom_terms": params.symptom_terms, "min_symptoms": params.min_symptoms},
    )
    return {"cohort": align(table, COHORT_SYMPTOMS)}
