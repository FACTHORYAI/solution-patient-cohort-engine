"""Parse and validate model answers before they become table rows."""

from __future__ import annotations

import json


def parse_items(answer: str) -> list[dict]:
    """Parse a model answer that must be a JSON array of objects."""
    try:
        items = json.loads(answer)
    except json.JSONDecodeError as error:
        message = f"model answer is not JSON: {error.msg} at position {error.pos}"
        raise ValueError(message) from error
    if not isinstance(items, list):
        message = "model answer is not a JSON array"
        raise ValueError(message)
    return [item for item in items if isinstance(item, dict)]


def validate_posology_item(item: dict) -> str:
    """Return the reason the relation row is rejected, or "" when it is valid."""
    for key in ("relation", "entity1", "chunk1", "entity2", "chunk2"):
        value = item.get(key)
        if not isinstance(value, str) or not value.strip():
            return f"missing or empty {key}"
    confidence = item.get("confidence")
    if not isinstance(confidence, (int, float)) or not 0 <= float(confidence) <= 1:
        return "confidence is not a number between 0 and 1"
    for key in ("rxnorm_code", "drug_resolution"):
        value = item.get(key)
        if value is not None and not isinstance(value, str):
            return f"{key} is not a string"
    return ""


def validate_entity_item(item: dict) -> str:
    """Return the reason the entity row is rejected, or "" when it is valid."""
    chunk = item.get("chunk")
    if not isinstance(chunk, str) or not chunk.strip():
        return "missing or empty chunk"
    ner_label = item.get("ner_label")
    if not isinstance(ner_label, str) or not ner_label.strip():
        return "missing or empty ner_label"
    sentence_id = item.get("sentence_id", 0)
    if not isinstance(sentence_id, int) or isinstance(sentence_id, bool) or sentence_id < 0:
        return "sentence_id is not a non-negative integer"
    return ""
