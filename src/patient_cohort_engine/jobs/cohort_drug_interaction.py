"""Patients who take a primary drug together with one of a family of interacting drugs."""

from __future__ import annotations

from dataclasses import dataclass

import pyarrow as pa

from patient_cohort_engine import io
from patient_cohort_engine.jobs._duck import align, run_query
from patient_cohort_engine.schemas import COHORT_DRUG_INTERACTION

INPUTS = ("graph_edges",)
OUTPUTS = ("cohort",)

NSAID_TERMS = (
    "ibuprofen,naproxen,diclofenac,indometacin,ketorolac,aspirin,ketoprofen,dexketoprofen,meloxicam"
)


@dataclass(frozen=True)
class Params:
    """Parameters for the drug-interaction cohort."""

    primary_drug: str = "warfarin"
    interacting_terms: str = NSAID_TERMS


def run(inputs: dict[str, pa.Table], params: Params) -> dict[str, pa.Table]:
    """Return the patients on the primary drug who also take an interacting drug."""
    if not params.primary_drug.strip():
        message = "Parameter primary_drug is empty; cohort_drug_interaction needs a drug name"
        raise ValueError(message)
    if not params.interacting_terms.strip():
        message = "Parameter interacting_terms is empty; cohort_drug_interaction needs terms"
        raise ValueError(message)
    table = run_query(
        io.read_sql("cohort_drug_interaction"),
        inputs,
        {"primary_drug": params.primary_drug, "interacting_terms": params.interacting_terms},
    )
    return {"cohort": align(table, COHORT_DRUG_INTERACTION)}
