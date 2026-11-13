"""PyArrow schemas for every table the jobs read or write."""

import pyarrow as pa

NOTES = pa.schema(
    [
        pa.field("note_id", pa.string()),
        pa.field("subject_id", pa.string()),
        pa.field("event_date", pa.date32()),
        pa.field("text", pa.string()),
        pa.field("gender", pa.string()),
        pa.field("date_of_birth", pa.date32()),
    ]
)

POSOLOGY = pa.schema(
    [
        pa.field("note_id", pa.string()),
        pa.field("subject_id", pa.string()),
        pa.field("event_date", pa.date32()),
        pa.field("relation", pa.string()),
        pa.field("entity1", pa.string()),
        pa.field("chunk1", pa.string()),
        pa.field("entity2", pa.string()),
        pa.field("chunk2", pa.string()),
        pa.field("confidence", pa.float64()),
        pa.field("rxnorm_code", pa.string()),
        pa.field("drug_resolution", pa.string()),
    ]
)

CLINICAL_ENTITIES = pa.schema(
    [
        pa.field("note_id", pa.string()),
        pa.field("subject_id", pa.string()),
        pa.field("event_date", pa.date32()),
        pa.field("sentence_id", pa.int32()),
        pa.field("chunk", pa.string()),
        pa.field("ner_label", pa.string()),
    ]
)

REJECTED_EXTRACTIONS = pa.schema(
    [
        pa.field("note_id", pa.string()),
        pa.field("subject_id", pa.string()),
        pa.field("event_date", pa.date32()),
        pa.field("reason", pa.string()),
        pa.field("model_answer", pa.string()),
    ]
)

# Graph tables, draft 0 (the shared contract for all solutions).
# graph_nodes: node_id is stable across runs and built as "<node_type>:<key>"; key is the
# natural key, with its code system where there is one (for example "rxnorm:11289").
GRAPH_NODES = pa.schema(
    [
        pa.field("node_id", pa.string()),
        pa.field("node_type", pa.string()),
        pa.field("key", pa.string()),
        pa.field("label", pa.string()),
        pa.field("properties", pa.string()),  # JSON text, only for things nobody filters on
    ]
)

# graph_edges: one fact per row. A fact points at another node (target_id) or holds a
# literal (value, with target_id null). Every node an edge names exists in graph_nodes.
# evidence_* ties the fact to the character span of a note; null when unknown.
GRAPH_EDGES = pa.schema(
    [
        pa.field("edge_id", pa.string()),  # stable: hash of source, relationship, target, evidence
        pa.field("source_id", pa.string()),
        pa.field("target_id", pa.string()),
        pa.field("relationship", pa.string()),
        pa.field("value", pa.string()),
        pa.field("valid_from", pa.date32()),
        pa.field("valid_to", pa.date32()),
        pa.field("evidence_document_id", pa.string()),
        pa.field("evidence_start", pa.int32()),
        pa.field("evidence_end", pa.int32()),
        pa.field("confidence", pa.float64()),
        pa.field("properties", pa.string()),
    ]
)

COHORT_DRUG = pa.schema(
    [
        pa.field("subject_id", pa.string()),
        pa.field("event_date", pa.date32()),
        pa.field("drug_name", pa.string()),
        pa.field("rxnorm_code", pa.string()),
        pa.field("details", pa.string()),
    ]
)

COHORT_DRUG_STRENGTH = pa.schema(
    [
        pa.field("subject_id", pa.string()),
        pa.field("event_date", pa.date32()),
        pa.field("drug_name", pa.string()),
        pa.field("rxnorm_code", pa.string()),
        pa.field("strength", pa.string()),
    ]
)

COHORT_DRUG_INTERACTION = pa.schema(
    [
        pa.field("subject_id", pa.string()),
        pa.field("event_date", pa.date32()),
        pa.field("primary_drug", pa.string()),
        pa.field("interacting_drugs", pa.list_(pa.string())),
    ]
)

COHORT_PROCEDURE = pa.schema(
    [
        pa.field("subject_id", pa.string()),
        pa.field("procedures", pa.list_(pa.string())),
    ]
)

COHORT_SYMPTOMS = pa.schema(
    [
        pa.field("subject_id", pa.string()),
        pa.field("event_date", pa.date32()),
        pa.field("symptoms", pa.list_(pa.string())),
    ]
)

COHORT_CONDITION = pa.schema(
    [
        pa.field("subject_id", pa.string()),
        pa.field("event_date", pa.date32()),
        pa.field("condition", pa.string()),
        pa.field("symptom", pa.string()),
    ]
)
