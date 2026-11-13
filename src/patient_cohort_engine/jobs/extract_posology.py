"""Extract drug-usage relations with RxNorm codes from clinical notes."""

from __future__ import annotations

from dataclasses import dataclass

import pyarrow as pa

from patient_cohort_engine import io
from patient_cohort_engine.jobs._duck import align
from patient_cohort_engine.schemas import POSOLOGY, REJECTED_EXTRACTIONS
from patient_cohort_engine.text.interface import TextModel
from patient_cohort_engine.text.parse import parse_items, validate_posology_item

INPUTS = ("notes",)
OUTPUTS = ("posology", "rejected_posology")


@dataclass(frozen=True)
class Params:
    """Parameters for posology extraction."""


def run(inputs: dict[str, pa.Table], params: Params, model: TextModel) -> dict[str, pa.Table]:
    """Return the drug-usage relations and every model answer that failed validation."""
    notes = inputs["notes"]
    instructions = io.read_prompt("posology")
    rows: list[dict] = []
    rejected: list[dict] = []
    for note in notes.to_pylist():
        answer = model.complete(instructions, note["text"])
        try:
            items = parse_items(answer)
        except ValueError as error:
            rejected.append(
                {
                    "note_id": note["note_id"],
                    "subject_id": note["subject_id"],
                    "event_date": note["event_date"],
                    "reason": str(error),
                    "model_answer": answer,
                }
            )
            items = []
        for item in items:
            reason = validate_posology_item(item)
            if reason:
                rejected.append(
                    {
                        "note_id": note["note_id"],
                        "subject_id": note["subject_id"],
                        "event_date": note["event_date"],
                        "reason": reason,
                        "model_answer": str(item),
                    }
                )
                continue
            rows.append(
                {
                    "note_id": note["note_id"],
                    "subject_id": note["subject_id"],
                    "event_date": note["event_date"],
                    "relation": item["relation"],
                    "entity1": item["entity1"],
                    "chunk1": item["chunk1"],
                    "entity2": item["entity2"],
                    "chunk2": item["chunk2"],
                    "confidence": float(item["confidence"]),
                    "rxnorm_code": item.get("rxnorm_code") or "",
                    "drug_resolution": item.get("drug_resolution") or "",
                }
            )
    return {
        "posology": align(pa.Table.from_pylist(rows, schema=POSOLOGY), POSOLOGY),
        "rejected_posology": align(
            pa.Table.from_pylist(rejected, schema=REJECTED_EXTRACTIONS), REJECTED_EXTRACTIONS
        ),
    }
