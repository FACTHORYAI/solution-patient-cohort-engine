"""PyArrow schemas for every table the jobs read or write."""

import pyarrow as pa

NOTES = pa.schema(
    [
        pa.field("subject_id", pa.string()),
        pa.field("event_date", pa.date32()),
        pa.field("text", pa.string()),
        pa.field("gender", pa.string()),
        pa.field("date_of_birth", pa.date32()),
    ]
)

POSOLOGY = pa.schema(
    [
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
        pa.field("subject_id", pa.string()),
        pa.field("event_date", pa.date32()),
        pa.field("sentence_id", pa.int32()),
        pa.field("chunk", pa.string()),
        pa.field("ner_label", pa.string()),
    ]
)

REJECTED_EXTRACTIONS = pa.schema(
    [
        pa.field("subject_id", pa.string()),
        pa.field("event_date", pa.date32()),
        pa.field("reason", pa.string()),
        pa.field("model_answer", pa.string()),
    ]
)

GRAPH_NODES = pa.schema(
    [
        pa.field("node_type", pa.string()),
        pa.field("name", pa.string()),
        pa.field("gender", pa.string()),
        pa.field("date_of_birth", pa.date32()),
    ]
)

GRAPH_EDGES = pa.schema(
    [
        pa.field("subject_id", pa.string()),
        pa.field("event_date", pa.date32()),
        pa.field("source_type", pa.string()),
        pa.field("source_name", pa.string()),
        pa.field("relationship", pa.string()),
        pa.field("target_type", pa.string()),
        pa.field("target_name", pa.string()),
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
