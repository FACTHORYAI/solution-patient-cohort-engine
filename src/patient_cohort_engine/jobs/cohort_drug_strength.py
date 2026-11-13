"""Patients whose drug has a strength relation at or above a dose in mg."""

from __future__ import annotations

from dataclasses import dataclass

import pyarrow as pa

from patient_cohort_engine import io
from patient_cohort_engine.jobs._duck import align, run_query
from patient_cohort_engine.schemas import COHORT_DRUG_STRENGTH

INPUTS = ("graph_edges",)
OUTPUTS = ("cohort",)


@dataclass(frozen=True)
class Params:
    """Parameters for the drug-strength cohort."""

    drug_name: str = ""
    min_strength_mg: float = 0.0


def run(inputs: dict[str, pa.Table], params: Params) -> dict[str, pa.Table]:
    """Return the patients whose drug strength is at least min_strength_mg."""
    if not params.drug_name.strip():
        message = "Parameter drug_name is empty; cohort_drug_strength needs a drug name"
        raise ValueError(message)
    table = run_query(
        io.read_sql("cohort_drug_strength"),
        inputs,
        {"drug_name": params.drug_name, "min_strength_mg": params.min_strength_mg},
    )
    return {"cohort": align(table, COHORT_DRUG_STRENGTH)}
