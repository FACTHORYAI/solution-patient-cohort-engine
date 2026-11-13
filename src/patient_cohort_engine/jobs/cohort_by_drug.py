"""Patients prescribed a drug, optionally within a date window."""

from __future__ import annotations

from dataclasses import dataclass

import pyarrow as pa

from patient_cohort_engine import io
from patient_cohort_engine.jobs._duck import align, run_query
from patient_cohort_engine.schemas import COHORT_DRUG

INPUTS = ("graph_nodes", "graph_edges")
OUTPUTS = ("cohort",)


@dataclass(frozen=True)
class Params:
    """Parameters for the drug cohort."""

    drug_name: str = ""
    start_date: str = ""
    end_date: str = ""


def run(inputs: dict[str, pa.Table], params: Params) -> dict[str, pa.Table]:
    """Return the patients prescribed the drug, with the date and RxNorm code."""
    if not params.drug_name.strip():
        message = "Parameter drug_name is empty; cohort_by_drug needs a drug name"
        raise ValueError(message)
    table = run_query(
        io.read_sql("cohort_by_drug"),
        inputs,
        {
            "drug_name": params.drug_name,
            "start_date": params.start_date,
            "end_date": params.end_date,
        },
    )
    return {"cohort": align(table, COHORT_DRUG)}
