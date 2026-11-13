"""Patients who had a named procedure."""

from __future__ import annotations

from dataclasses import dataclass

import pyarrow as pa

from patient_cohort_engine import io
from patient_cohort_engine.jobs._duck import align, run_query
from patient_cohort_engine.schemas import COHORT_PROCEDURE

INPUTS = ("clinical_entities",)
OUTPUTS = ("cohort",)


@dataclass(frozen=True)
class Params:
    """Parameters for the procedure cohort."""

    procedure_terms: str = ""


def run(inputs: dict[str, pa.Table], params: Params) -> dict[str, pa.Table]:
    """Return the patients who had one of the named procedures, with their names."""
    if not params.procedure_terms.strip():
        message = "Parameter procedure_terms is empty; cohort_by_procedure needs terms"
        raise ValueError(message)
    table = run_query(
        io.read_sql("cohort_by_procedure"),
        inputs,
        {"procedure_terms": params.procedure_terms},
    )
    return {"cohort": align(table, COHORT_PROCEDURE)}
