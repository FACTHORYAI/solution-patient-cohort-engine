"""Extract clinical entities (symptoms, procedures, tests and more) from notes."""

from __future__ import annotations

from dataclasses import dataclass

import pyarrow as pa

from patient_cohort_engine import io
from patient_cohort_engine.jobs._duck import align
from patient_cohort_engine.schemas import CLINICAL_ENTITIES, REJECTED_EXTRACTIONS
from patient_cohort_engine.text.interface import TextModel
from patient_cohort_engine.text.parse import parse_items, validate_entity_item

INPUTS = ("notes",)
OUTPUTS = ("clinical_entities", "rejected_entities")


@dataclass(frozen=True)
class Params:
    """Parameters for clinical entity extraction."""


def run(inputs: dict[str, pa.Table], params: Params, model: TextModel) -> dict[str, pa.Table]:
    """Return the clinical entities and every model answer that failed validation."""
    notes = inputs["notes"]
    instructions = io.read_prompt("clinical_entities")
    rows: list[dict] = []
    rejected: list[dict] = []
    for note in notes.to_pylist():
        answer = model.complete(instructions, note["text"])
        try:
            items = parse_items(answer)
        except ValueError as error:
            rejected.append(
                {
                    "subject_id": note["subject_id"],
                    "event_date": note["event_date"],
                    "reason": str(error),
                    "model_answer": answer,
                }
            )
            items = []
        for item in items:
            reason = validate_entity_item(item)
            if reason:
                rejected.append(
                    {
                        "subject_id": note["subject_id"],
                        "event_date": note["event_date"],
                        "reason": reason,
                        "model_answer": str(item),
                    }
                )
                continue
            rows.append(
                {
                    "subject_id": note["subject_id"],
                    "event_date": note["event_date"],
                    "sentence_id": int(item.get("sentence_id", 0)),
                    "chunk": item["chunk"],
                    "ner_label": item["ner_label"],
                }
            )
    return {
        "clinical_entities": align(
            pa.Table.from_pylist(rows, schema=CLINICAL_ENTITIES), CLINICAL_ENTITIES
        ),
        "rejected_entities": align(
            pa.Table.from_pylist(rejected, schema=REJECTED_EXTRACTIONS), REJECTED_EXTRACTIONS
        ),
    }
