"""Generate the synthetic sample: invented clinical notes and the rows extracted from them.

Everything here is invented. No real patient, note or record is used. The notes are put
together from sentence templates and small clinical vocabularies; the rows an extraction
model would return are written from the same templates, so they are exact. Run it from the
repository root:

    uv run python data/generate_sample.py

It writes data/sample/*.parquet (notes, posology, clinical_entities, graph_nodes,
graph_edges) and tests/recorded_answers.json. The same seed always gives the same files.
"""

from __future__ import annotations

import datetime as dt
import json
import random
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from patient_cohort_engine.jobs import REGISTRY, call_run
from patient_cohort_engine.schemas import CLINICAL_ENTITIES, NOTES, POSOLOGY

SEED = 20251101
N_PATIENTS = 48
FIRST_DAY = dt.date(2023, 2, 1)
LAST_DAY = dt.date(2025, 10, 31)
REPO = Path(__file__).resolve().parent.parent

# drug -> (illustrative RxNorm code, mention aliases, strengths, frequencies, route phrase)
# fmt: off
DRUGS: dict[str, tuple[str, list[str], list[str], list[str], str]] = {
    "warfarin": ("11289", ["warfarin", "coumadin"], ["2 mg", "3 mg", "5 mg"], ["daily"], "orally"),
    "apixaban": ("1364430", ["apixaban", "eliquis"], ["2.5 mg", "5 mg"], ["twice daily"], ""),
    "aspirin": ("1191", ["aspirin"], ["81 mg"], ["once daily"], ""),
    "clopidogrel": ("32968", ["clopidogrel"], ["75 mg"], ["once daily"], ""),
    "ibuprofen": ("5640", ["ibuprofen", "motrin"], ["400 mg", "600 mg"], ["as needed"], ""),
    "naproxen": ("7258", ["naproxen"], ["250 mg", "500 mg"], ["twice daily"], "orally"),
    "diclofenac": ("3355", ["diclofenac"], ["50 mg"], ["twice daily"], ""),
    "acetaminophen": ("161", ["acetaminophen", "tylenol"], ["500 mg", "650 mg"], ["as needed"], ""),
    "lisinopril": ("29046", ["lisinopril"], ["10 mg", "20 mg", "40 mg"], ["once daily"], ""),
    "losartan": ("52175", ["losartan"], ["50 mg", "100 mg"], ["once daily"], ""),
    "amlodipine": ("17767", ["amlodipine"], ["5 mg", "10 mg"], ["once daily"], ""),
    "hydrochlorothiazide": ("5487", ["hydrochlorothiazide"], ["12.5 mg", "25 mg"], ["daily"], ""),
    "metoprolol": ("6918", ["metoprolol"], ["25 mg", "50 mg"], ["twice daily"], "by mouth"),
    "carvedilol": ("20352", ["carvedilol"], ["6.25 mg", "12.5 mg"], ["twice daily"], ""),
    "furosemide": ("4603", ["furosemide", "lasix"], ["20 mg", "40 mg"], ["once daily"], ""),
    "spironolactone": ("9997", ["spironolactone"], ["25 mg"], ["once daily"], ""),
    "isosorbide": ("6056", ["isosorbide"], ["20 mg", "30 mg"], ["twice daily"], ""),
    "atorvastatin": ("83367", ["atorvastatin", "lipitor"], ["20 mg", "40 mg"], ["at bedtime"], ""),
    "simvastatin": ("36567", ["simvastatin"], ["20 mg", "40 mg"], ["at bedtime"], ""),
    "metformin": ("6809", ["metformin"], ["500 mg", "1000 mg"], ["twice daily"], "orally"),
    "glipizide": ("4821", ["glipizide"], ["5 mg", "10 mg"], ["once daily"], ""),
    "empagliflozin": ("1545653", ["empagliflozin", "jardiance"], ["10 mg", "25 mg"], ["daily"], ""),
    "levothyroxine": ("10582", ["levothyroxine"], ["50 mcg", "75 mcg", "100 mcg"], ["every morning"], ""),
    "omeprazole": ("7646", ["omeprazole"], ["20 mg", "40 mg"], ["once daily"], ""),
    "albuterol": ("435", ["albuterol"], ["90 mcg"], ["as needed"], "inhaled"),
    "prednisone": ("8640", ["prednisone"], ["20 mg", "40 mg"], ["once daily"], ""),
    "sertraline": ("36437", ["sertraline", "zoloft"], ["50 mg", "100 mg"], ["once daily"], ""),
    "amoxicillin": ("723", ["amoxicillin"], ["500 mg"], ["three times daily"], "orally"),
}
# fmt: on

# condition -> symptoms, body parts, tests, drug options (one is picked), reason words
# fmt: off
CONDITIONS: dict[str, dict[str, list[str]]] = {
    "hypertension": {
        "symptoms": ["headache", "dizziness"],
        "body": ["chest"],
        "tests": ["blood pressure"],
        "drugs": ["lisinopril", "losartan", "amlodipine", "hydrochlorothiazide"],
    },
    "type 2 diabetes": {
        "symptoms": ["increased thirst", "fatigue", "blurred vision"],
        "body": ["feet"],
        "tests": ["HbA1c", "glucose"],
        "drugs": ["metformin", "glipizide", "empagliflozin"],
    },
    "atrial fibrillation": {
        "symptoms": ["palpitations", "dizziness", "chest pain"],
        "body": ["chest"],
        "tests": ["INR", "ECG"],
        "drugs": ["warfarin", "apixaban"],
    },
    "heart failure": {
        "symptoms": ["shortness of breath", "leg swelling", "fatigue"],
        "body": ["legs", "chest"],
        "tests": ["echocardiogram", "BNP"],
        "drugs": ["furosemide", "carvedilol", "spironolactone"],
    },
    "coronary artery disease": {
        "symptoms": ["chest pain", "shortness of breath"],
        "body": ["chest"],
        "tests": ["ECG", "troponin"],
        "drugs": ["aspirin", "clopidogrel", "isosorbide"],
    },
    "hyperlipidemia": {
        "symptoms": ["fatigue"],
        "body": ["abdomen"],
        "tests": ["lipid panel"],
        "drugs": ["atorvastatin", "simvastatin"],
    },
    "hypothyroidism": {
        "symptoms": ["fatigue", "weight gain", "cold intolerance"],
        "body": ["neck"],
        "tests": ["TSH"],
        "drugs": ["levothyroxine"],
    },
    "asthma": {
        "symptoms": ["wheezing", "cough", "shortness of breath"],
        "body": ["lungs"],
        "tests": ["spirometry"],
        "drugs": ["albuterol"],
    },
    "gastroesophageal reflux disease": {
        "symptoms": ["heartburn", "nausea"],
        "body": ["abdomen"],
        "tests": ["endoscopy"],
        "drugs": ["omeprazole"],
    },
    "osteoarthritis": {
        "symptoms": ["joint pain", "stiffness"],
        "body": ["knee", "hip", "lower back"],
        "tests": ["knee x-ray"],
        "drugs": ["ibuprofen", "naproxen", "diclofenac", "acetaminophen"],
    },
    "depression": {
        "symptoms": ["low mood", "insomnia"],
        "body": [],
        "tests": ["PHQ-9"],
        "drugs": ["sertraline"],
    },
    "chronic kidney disease": {
        "symptoms": ["fatigue", "nausea"],
        "body": ["abdomen"],
        "tests": ["creatinine"],
        "drugs": [],
    },
}
# fmt: on

LAB_TESTS = {
    "INR",
    "HbA1c",
    "glucose",
    "BNP",
    "troponin",
    "creatinine",
    "TSH",
    "lipid panel",
    "blood pressure",
}
PROCEDURES = [
    "hernia repair",
    "appendectomy",
    "cholecystectomy",
    "knee replacement",
    "hip replacement",
    "cardiac catheterization",
    "coronary artery bypass graft",
    "colonoscopy",
    "cataract surgery",
]
# Conditions that tend to go together, so the sample has realistic overlaps.
COMORBID = {
    "hypertension": [
        "type 2 diabetes",
        "hyperlipidemia",
        "heart failure",
        "chronic kidney disease",
    ],
    "atrial fibrillation": ["hypertension", "heart failure", "osteoarthritis"],
    "coronary artery disease": ["hypertension", "hyperlipidemia", "type 2 diabetes"],
    "osteoarthritis": ["hypertension", "atrial fibrillation", "depression"],
}
# Patients written by hand so the demo questions always have answers:
# (conditions, forced drugs, forced procedure)
# fmt: off
SCENARIOS: list[tuple[list[str], list[str], str]] = [
    (["atrial fibrillation", "osteoarthritis"], ["warfarin", "ibuprofen"], "hernia repair"),
    (["atrial fibrillation", "osteoarthritis"], ["warfarin", "naproxen"], "appendectomy"),
    (["atrial fibrillation", "hypertension"], ["warfarin", "lisinopril"], "cholecystectomy"),
    (["atrial fibrillation", "coronary artery disease"], ["apixaban", "aspirin"], ""),
    (["coronary artery disease", "hypertension", "type 2 diabetes"], [], "cardiac catheterization"),
    (["heart failure", "hypertension"], ["furosemide"], ""),
]
# fmt: on


def _list_text(items: list[str]) -> str:
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def _make_patients(rng: random.Random) -> list[dict]:
    patients = []
    for index in range(N_PATIENTS):
        if index < len(SCENARIOS):
            conditions, forced, procedure = SCENARIOS[index]
            conditions = list(conditions)
        else:
            first = rng.choice(list(CONDITIONS))
            conditions = [first]
            for _ in range(rng.choice([0, 1, 1, 2])):
                options = [c for c in COMORBID.get(first, list(CONDITIONS)) if c not in conditions]
                if options:
                    conditions.append(rng.choice(options))
            forced = []
            procedure = rng.choice(PROCEDURES) if rng.random() < 0.3 else ""
        drugs = list(forced)
        for condition in conditions:
            options = CONDITIONS[condition]["drugs"]
            if options and not any(d in options for d in drugs):
                drugs.append(rng.choice(options))
        age = rng.randint(38, 86)
        patients.append(
            {
                "subject_id": str(10001 + index),
                "gender": rng.choice(["M", "F"]),
                "date_of_birth": dt.date(2025, 1, 1)
                - dt.timedelta(days=age * 365 + rng.randint(0, 364)),
                "conditions": conditions,
                "drugs": drugs,
                "procedure": procedure,
                "strength": {d: rng.randrange(len(DRUGS[d][2])) for d in drugs},
                "alias": {d: rng.choice(DRUGS[d][1]) for d in drugs},
            }
        )
    return patients


def _visit_dates(rng: random.Random) -> list[dt.date]:
    day = FIRST_DAY + dt.timedelta(days=rng.randint(0, 420))
    dates = []
    for _ in range(rng.randint(2, 4)):
        if day > LAST_DAY:
            break
        dates.append(day)
        day += dt.timedelta(days=rng.randint(70, 260))
    return dates


def _confidence(rng: random.Random) -> float:
    return round(rng.uniform(0.84, 0.99), 2)


def _write_note(rng: random.Random, patient: dict, visit: int, short_course: str) -> dict:
    """Build one note and the rows an extraction model would return for it."""
    sentences: list[str] = []
    entities: list[dict] = []
    posology: list[dict] = []

    def add_entity(chunk: str, label: str, sentence_id: int) -> None:
        if not any(e["chunk"] == chunk and e["ner_label"] == label for e in entities):
            entities.append({"sentence_id": sentence_id, "chunk": chunk, "ner_label": label})

    conditions = patient["conditions"]
    pool = sorted({s for c in conditions for s in CONDITIONS[c]["symptoms"]})
    symptoms = rng.sample(pool, k=min(len(pool), rng.choice([1, 2, 2, 3])))
    opener = rng.choice(["Patient presents with", "Patient reports", "Patient complains of"])
    sentences.append(f"{opener} {_list_text(symptoms)}.")
    for symptom in symptoms:
        add_entity(symptom, "Symptom", 0)

    sentences.append(f"{rng.choice(['History of', 'Known'])} {_list_text(conditions)}.")
    for condition in conditions:
        add_entity(condition, "Disease_Syndrome_Disorder", 1)

    bodies = [b for c in conditions for b in CONDITIONS[c]["body"]]
    if bodies:
        body = rng.choice(bodies)
        finding = rng.choice(["unremarkable", "tender on palpation", "normal"])
        sentences.append(f"Examination of the {body} was {finding}.")
        add_entity(body, "Body_Part", len(sentences) - 1)

    tests = [t for c in conditions for t in CONDITIONS[c]["tests"]]
    if tests:
        test = rng.choice(tests)
        outcomes = ["Ordered {t}.", "Reviewed {t}, which was normal."]
        if test in LAB_TESTS:
            outcomes.append("Reviewed {t}, which was elevated.")
        sentences.append(rng.choice(outcomes).format(t=test))
        add_entity(test, "Test", len(sentences) - 1)

    if patient["procedure"] and visit == 0:
        procedure = patient["procedure"]
        when = rng.choice(["last year", "two years ago", "last month"])
        sentences.append(f"Underwent {procedure} {when}.")
        add_entity(procedure, "Procedure", len(sentences) - 1)
    elif visit == 1 and rng.random() < 0.25:
        procedure = rng.choice(PROCEDURES)
        sentences.append(f"Underwent {procedure} since the last visit.")
        add_entity(procedure, "Procedure", len(sentences) - 1)

    medications = list(patient["drugs"])
    if short_course:
        medications.append(short_course)
    for drug in medications:
        code, _aliases, strengths, frequencies, route = DRUGS[drug]
        if drug in patient["strength"]:
            if visit > 0 and rng.random() < 0.3 and len(strengths) > 1:
                patient["strength"][drug] = rng.randrange(len(strengths))
            strength = strengths[patient["strength"][drug]]
            alias = patient["alias"][drug]
            verb = rng.choice(["Takes", "Continues", "Maintained on"])
        else:  # a short course, prescribed at this visit only
            strength = strengths[0]
            alias = drug
            verb = "Prescribed"
        frequency = rng.choice(frequencies)
        parts = [verb, alias, strength]
        relations = [("STRENGTH", strength), ("FREQUENCY", frequency)]
        if route:
            parts.append(route)
            relations.insert(1, ("ROUTE", route))
        parts.append(frequency)
        if drug not in patient["strength"]:  # a short course has a duration
            days = f"{rng.choice([5, 7, 10])} days"
            parts.append(f"for {days}")
            relations.append(("DURATION", days))
        reason_pool = [c for c in conditions if drug in CONDITIONS[c]["drugs"]]
        if drug == "prednisone":
            reason_pool = ["asthma"] if "asthma" in conditions else []
        if drug == "amoxicillin":
            reason_pool = ["sinusitis"]
        if reason_pool and rng.random() < 0.5:
            reason = reason_pool[0]
            parts.append(f"for {reason}")
            relations.append(("REASON", reason))
            add_entity(reason, "Disease_Syndrome_Disorder", len(sentences))
        sentences.append(" ".join(parts) + ".")
        for relation, chunk in relations:
            posology.append(
                {
                    "relation": f"DRUG-{relation}",
                    "entity1": "DRUG",
                    "chunk1": alias,
                    "entity2": relation,
                    "chunk2": chunk,
                    "confidence": _confidence(rng),
                    "rxnorm_code": code,
                    "drug_resolution": drug,
                }
            )
    return {"text": " ".join(sentences), "entities": entities, "posology": posology}


def generate() -> dict[str, list[dict]]:
    rng = random.Random(SEED)
    notes: list[dict] = []
    posology: list[dict] = []
    entities: list[dict] = []
    answers: dict[str, dict[str, str]] = {"posology": {}, "clinical_entities": {}}
    for patient in _make_patients(rng):
        for visit, day in enumerate(_visit_dates(rng)):
            short_course = ""
            if visit > 0 and rng.random() < 0.12:
                short_course = rng.choice(["amoxicillin", "prednisone"])
                if short_course == "prednisone" and "asthma" not in patient["conditions"]:
                    short_course = "amoxicillin"
            note = _write_note(rng, patient, visit, short_course)
            note_id = f"note-{len(notes) + 1:04d}"
            notes.append(
                {
                    "note_id": note_id,
                    "subject_id": patient["subject_id"],
                    "event_date": day,
                    "text": note["text"],
                    "gender": patient["gender"],
                    "date_of_birth": patient["date_of_birth"],
                }
            )
            for row in note["posology"]:
                posology.append(
                    {
                        "note_id": note_id,
                        "subject_id": patient["subject_id"],
                        "event_date": day,
                        **row,
                    }
                )
            for row in note["entities"]:
                entities.append(
                    {
                        "note_id": note_id,
                        "subject_id": patient["subject_id"],
                        "event_date": day,
                        **row,
                    }
                )
            answers["posology"][note["text"]] = json.dumps(note["posology"])
            answers["clinical_entities"][note["text"]] = json.dumps(note["entities"])
    return {"notes": notes, "posology": posology, "clinical_entities": entities, "answers": answers}


def main() -> None:
    data = generate()
    tables = {
        "notes": pa.Table.from_pylist(data["notes"], schema=NOTES),
        "posology": pa.Table.from_pylist(data["posology"], schema=POSOLOGY),
        "clinical_entities": pa.Table.from_pylist(
            data["clinical_entities"], schema=CLINICAL_ENTITIES
        ),
    }
    spec = REGISTRY["build_knowledge_graph"]
    tables.update(call_run(spec, tables, spec.params_cls(), None))
    sample_dir = REPO / "data" / "sample"
    for name, table in tables.items():
        pq.write_table(table, sample_dir / f"{name}.parquet")
        print(f"{name}: {table.num_rows} rows")
    answers_path = REPO / "tests" / "recorded_answers.json"
    answers_path.write_text(json.dumps(data["answers"], indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
