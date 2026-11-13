"""Patients who had a named symptom on a date they also carried a named condition."""

from __future__ import annotations

from dataclasses import dataclass

import pyarrow as pa

from patient_cohort_engine import io
from patient_cohort_engine.jobs._duck import align, run_query
from patient_cohort_engine.schemas import COHORT_CONDITION

INPUTS = ("clinical_entities",)
OUTPUTS = ("cohort",)


@dataclass(frozen=True)
class Params:
    """Parameters for the condition cohort."""

    condition_terms: str = ""
    symptom_term: str = ""


def run(inputs: dict[str, pa.Table], params: Params) -> dict[str, pa.Table]:
    """Return the patients with a condition and the named symptom on the same date."""
    if not params.condition_terms.strip():
        message = "Parameter condition_terms is empty; cohort_by_condition needs terms"
        raise ValueError(message)
    if not params.symptom_term.strip():
        message = "Parameter symptom_term is empty; cohort_by_condition needs a symptom"
        raise ValueError(message)
    table = run_query(
        io.read_sql("cohort_by_condition"),
        inputs,
        {"condition_terms": params.condition_terms, "symptom_term": params.symptom_term},
    )
    return {"cohort": align(table, COHORT_CONDITION)}
