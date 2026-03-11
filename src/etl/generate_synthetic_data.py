"""
Synthetic Healthcare Data Generator for CarePulse.

Generates realistic Synthea-style CSV files:
  - patients.csv
  - encounters.csv
  - conditions.csv
  - procedures.csv
  - medications.csv
  - providers.csv
  - organizations.csv

This replaces the need to download or install Synthea.
All data is fake but follows realistic healthcare patterns.
"""

import uuid
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from src.config import DATA_RAW

# Seed for reproducibility
random.seed(42)
np.random.seed(42)

# ---------------------------------------------------------------------------
# Configuration — adjust these to change dataset size
# ---------------------------------------------------------------------------
NUM_PATIENTS = 1000
NUM_PROVIDERS = 40
NUM_ORGANIZATIONS = 8
ENCOUNTER_YEARS = (2021, 2024)  # encounters span these years
AVG_ENCOUNTERS_PER_PATIENT = 6

# ---------------------------------------------------------------------------
# Realistic reference data
# ---------------------------------------------------------------------------
FIRST_NAMES_M = ["James", "Robert", "John", "Michael", "David", "William",
                 "Richard", "Joseph", "Thomas", "Charles", "Daniel", "Matthew"]
FIRST_NAMES_F = ["Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth",
                 "Susan", "Jessica", "Sarah", "Karen", "Lisa", "Nancy"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
              "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez",
              "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore",
              "Jackson", "Martin", "Lee", "Perez", "Thompson", "White"]

RACES = ["White", "Black", "Asian", "Hispanic", "Native", "Other"]
RACE_WEIGHTS = [0.58, 0.13, 0.06, 0.18, 0.02, 0.03]

ETHNICITIES = ["Non-Hispanic", "Hispanic"]
ETHNICITY_WEIGHTS = [0.82, 0.18]

STATES = ["CA", "TX", "NY", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]
CITIES = {
    "CA": ["Los Angeles", "San Francisco", "San Diego", "Sacramento"],
    "TX": ["Houston", "Dallas", "Austin", "San Antonio"],
    "NY": ["New York", "Buffalo", "Rochester", "Albany"],
    "FL": ["Miami", "Orlando", "Tampa", "Jacksonville"],
    "IL": ["Chicago", "Springfield", "Naperville", "Peoria"],
    "PA": ["Philadelphia", "Pittsburgh", "Allentown", "Erie"],
    "OH": ["Columbus", "Cleveland", "Cincinnati", "Toledo"],
    "GA": ["Atlanta", "Savannah", "Augusta", "Macon"],
    "NC": ["Charlotte", "Raleigh", "Durham", "Greensboro"],
    "MI": ["Detroit", "Grand Rapids", "Ann Arbor", "Lansing"],
}

SPECIALTIES = ["General Practice", "Internal Medicine", "Cardiology",
               "Pulmonology", "Orthopedics", "Neurology", "Emergency Medicine",
               "Family Medicine", "Endocrinology", "Oncology"]

ENCOUNTER_CLASSES = ["inpatient", "outpatient", "emergency", "wellness", "ambulatory"]
ENCOUNTER_CLASS_WEIGHTS = [0.15, 0.35, 0.12, 0.20, 0.18]

PAYERS = ["Medicare", "Medicaid", "Blue Cross", "Aetna", "UnitedHealth",
           "Cigna", "Humana", "Self-Pay"]
PAYER_WEIGHTS = [0.25, 0.15, 0.15, 0.10, 0.15, 0.08, 0.07, 0.05]

# Chronic conditions (SNOMED-style codes with descriptions)
CHRONIC_CONDITIONS = [
    ("44054006", "Diabetes mellitus type 2"),
    ("38341003", "Hypertensive disorder"),
    ("53741008", "Coronary heart disease"),
    ("195967001", "Asthma"),
    ("13645005", "Chronic obstructive pulmonary disease"),
    ("235595009", "Chronic kidney disease"),
    ("40055000", "Chronic sinusitis"),
    ("82423001", "Chronic pain syndrome"),
    ("66071002", "Viral hepatitis type B"),
    ("73211009", "Diabetes mellitus"),
]

ACUTE_CONDITIONS = [
    ("10509002", "Acute bronchitis"),
    ("195662009", "Acute viral pharyngitis"),
    ("36971009", "Sinusitis"),
    ("444814009", "Viral sinusitis"),
    ("43878008", "Streptococcal sore throat"),
    ("68496003", "Polyp of colon"),
    ("283385000", "Laceration of hand"),
    ("75498004", "Acute bacterial sinusitis"),
    ("65363002", "Otitis media"),
    ("87433001", "Pulmonary emphysema"),
    ("370247008", "Facial laceration"),
    ("403190006", "Contact dermatitis"),
]

PROCEDURES = [
    ("710824005", "Assessment of health and social care needs"),
    ("430193006", "Medication reconciliation"),
    ("713106006", "Evaluation of care plan"),
    ("171207006", "Depression screening"),
    ("252160004", "Standard electrocardiogram"),
    ("76601001", "Intubation"),
    ("23426006", "Measurement of respiratory function"),
    ("268556000", "Physical examination"),
    ("308335008", "Patient encounter procedure"),
    ("73761001", "Colonoscopy"),
]

MEDICATIONS = [
    ("860975", "Metformin 500 MG"),
    ("316672", "Simvastatin 20 MG"),
    ("197361", "Amlodipine 5 MG"),
    ("310798", "Hydrochlorothiazide 25 MG"),
    ("198440", "Lisinopril 10 MG"),
    ("849574", "Naproxen sodium 220 MG"),
    ("308136", "Amoxicillin 500 MG"),
    ("311995", "Ibuprofen 200 MG"),
    ("312961", "Acetaminophen 325 MG"),
    ("834101", "Omeprazole 20 MG"),
]

FACILITY_NAMES = [
    "Mercy General Hospital",
    "St. Luke's Medical Center",
    "Community Health System",
    "Valley Regional Hospital",
    "Riverside Medical Center",
    "Metro Health Hospital",
    "Summit Care Hospital",
    "Pinnacle Health Center",
]


def _uuid() -> str:
    return str(uuid.uuid4())


def _random_date(start_year: int, end_year: int) -> datetime:
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


# ---------------------------------------------------------------------------
# Generate organizations
# ---------------------------------------------------------------------------
def generate_organizations() -> pd.DataFrame:
    rows = []
    for i in range(NUM_ORGANIZATIONS):
        state = random.choice(STATES)
        rows.append({
            "id": _uuid(),
            "name": FACILITY_NAMES[i % len(FACILITY_NAMES)],
            "city": random.choice(CITIES[state]),
            "state": state,
            "zip": f"{random.randint(10000, 99999)}",
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Generate providers
# ---------------------------------------------------------------------------
def generate_providers(org_ids: list[str]) -> pd.DataFrame:
    rows = []
    for _ in range(NUM_PROVIDERS):
        gender = random.choice(["M", "F"])
        first = random.choice(FIRST_NAMES_M if gender == "M" else FIRST_NAMES_F)
        last = random.choice(LAST_NAMES)
        rows.append({
            "id": _uuid(),
            "name": f"Dr. {first} {last}",
            "specialty": random.choice(SPECIALTIES),
            "org_id": random.choice(org_ids),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Generate patients
# ---------------------------------------------------------------------------
def generate_patients() -> pd.DataFrame:
    rows = []
    for _ in range(NUM_PATIENTS):
        gender = random.choice(["M", "F"])
        first = random.choice(FIRST_NAMES_M if gender == "M" else FIRST_NAMES_F)
        last = random.choice(LAST_NAMES)
        state = random.choice(STATES)
        birth = _random_date(1940, 2005)

        # ~5% of patients have a death date
        death = None
        if random.random() < 0.05:
            death = birth + timedelta(days=random.randint(20000, 30000))
            if death > datetime(2024, 12, 31):
                death = None

        rows.append({
            "id": _uuid(),
            "birth_date": birth.date(),
            "death_date": death.date() if death else None,
            "gender": gender,
            "race": random.choices(RACES, weights=RACE_WEIGHTS, k=1)[0],
            "ethnicity": random.choices(ETHNICITIES, weights=ETHNICITY_WEIGHTS, k=1)[0],
            "city": random.choice(CITIES[state]),
            "state": state,
            "zip": f"{random.randint(10000, 99999)}",
            "county": f"{random.choice(CITIES[state])} County",
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Generate encounters for each patient
# ---------------------------------------------------------------------------
def generate_encounters(patient_ids: list[str],
                        provider_ids: list[str],
                        org_ids: list[str]) -> pd.DataFrame:
    rows = []
    for pid in patient_ids:
        # Each patient gets a variable number of encounters
        n_enc = max(1, int(np.random.poisson(AVG_ENCOUNTERS_PER_PATIENT)))
        for _ in range(n_enc):
            enc_class = random.choices(
                ENCOUNTER_CLASSES, weights=ENCOUNTER_CLASS_WEIGHTS, k=1
            )[0]
            start = _random_date(ENCOUNTER_YEARS[0], ENCOUNTER_YEARS[1])

            # Length of stay depends on encounter type
            if enc_class == "inpatient":
                los_days = max(1, int(np.random.exponential(4)))
            elif enc_class == "emergency":
                los_days = max(0, int(np.random.exponential(0.5)))
            else:
                los_days = 0

            end = start + timedelta(days=los_days, hours=random.randint(1, 12))

            # Cost depends on encounter type
            if enc_class == "inpatient":
                cost = round(random.uniform(5000, 80000), 2)
            elif enc_class == "emergency":
                cost = round(random.uniform(500, 15000), 2)
            else:
                cost = round(random.uniform(50, 2000), 2)

            rows.append({
                "id": _uuid(),
                "patient_id": pid,
                "provider_id": random.choice(provider_ids),
                "org_id": random.choice(org_ids),
                "payer": random.choices(PAYERS, weights=PAYER_WEIGHTS, k=1)[0],
                "encounter_class": enc_class,
                "start_date": start,
                "end_date": end,
                "total_cost": cost,
                "reason_description": random.choice(
                    CHRONIC_CONDITIONS + ACUTE_CONDITIONS
                )[1],
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Generate conditions for each encounter
# ---------------------------------------------------------------------------
def generate_conditions(encounters_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, enc in encounters_df.iterrows():
        # 1-3 conditions per encounter
        n_cond = random.randint(1, 3)
        chosen = random.sample(
            CHRONIC_CONDITIONS + ACUTE_CONDITIONS,
            min(n_cond, len(CHRONIC_CONDITIONS) + len(ACUTE_CONDITIONS)),
        )
        for code, desc in chosen:
            onset = enc["start_date"] - timedelta(days=random.randint(0, 365))
            # Chronic conditions often unresolved
            resolved = None
            if desc not in [c[1] for c in CHRONIC_CONDITIONS]:
                if random.random() < 0.7:
                    resolved = enc["end_date"] + timedelta(days=random.randint(0, 30))

            rows.append({
                "patient_id": enc["patient_id"],
                "encounter_id": enc["id"],
                "code": code,
                "description": desc,
                "onset_date": onset.date() if hasattr(onset, 'date') else onset,
                "resolved_date": resolved.date() if resolved and hasattr(resolved, 'date') else resolved,
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Generate procedures for a subset of encounters
# ---------------------------------------------------------------------------
def generate_procedures(encounters_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, enc in encounters_df.iterrows():
        if random.random() < 0.6:  # 60% of encounters have a procedure
            n_proc = random.randint(1, 2)
            chosen = random.sample(PROCEDURES, min(n_proc, len(PROCEDURES)))
            for code, desc in chosen:
                rows.append({
                    "patient_id": enc["patient_id"],
                    "encounter_id": enc["id"],
                    "code": code,
                    "description": desc,
                    "date": enc["start_date"].date() if hasattr(enc["start_date"], 'date') else enc["start_date"],
                    "cost": round(random.uniform(100, 5000), 2),
                })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Generate medications for a subset of encounters
# ---------------------------------------------------------------------------
def generate_medications(encounters_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, enc in encounters_df.iterrows():
        if random.random() < 0.5:  # 50% of encounters have medications
            n_med = random.randint(1, 3)
            chosen = random.sample(MEDICATIONS, min(n_med, len(MEDICATIONS)))
            for code, desc in chosen:
                start = enc["start_date"]
                # Some medications are ongoing
                stop = None
                if random.random() < 0.6:
                    stop = start + timedelta(days=random.randint(7, 180))

                rows.append({
                    "patient_id": enc["patient_id"],
                    "encounter_id": enc["id"],
                    "code": code,
                    "description": desc,
                    "start_date": start.date() if hasattr(start, 'date') else start,
                    "stop_date": stop.date() if stop and hasattr(stop, 'date') else stop,
                    "cost": round(random.uniform(5, 500), 2),
                })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Main: generate all data and save to CSV
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("CarePulse — Synthetic Data Generator")
    print("=" * 60)

    DATA_RAW.mkdir(parents=True, exist_ok=True)

    print(f"\n[1/7] Generating {NUM_ORGANIZATIONS} organizations...")
    orgs = generate_organizations()
    orgs.to_csv(DATA_RAW / "organizations.csv", index=False)
    print(f"       → {len(orgs)} organizations saved")

    print(f"[2/7] Generating {NUM_PROVIDERS} providers...")
    providers = generate_providers(orgs["id"].tolist())
    providers.to_csv(DATA_RAW / "providers.csv", index=False)
    print(f"       → {len(providers)} providers saved")

    print(f"[3/7] Generating {NUM_PATIENTS} patients...")
    patients = generate_patients()
    patients.to_csv(DATA_RAW / "patients.csv", index=False)
    print(f"       → {len(patients)} patients saved")

    print("[4/7] Generating encounters...")
    encounters = generate_encounters(
        patients["id"].tolist(),
        providers["id"].tolist(),
        orgs["id"].tolist(),
    )
    encounters.to_csv(DATA_RAW / "encounters.csv", index=False)
    print(f"       → {len(encounters)} encounters saved")

    print("[5/7] Generating conditions...")
    conditions = generate_conditions(encounters)
    conditions.to_csv(DATA_RAW / "conditions.csv", index=False)
    print(f"       → {len(conditions)} conditions saved")

    print("[6/7] Generating procedures...")
    procedures = generate_procedures(encounters)
    procedures.to_csv(DATA_RAW / "procedures.csv", index=False)
    print(f"       → {len(procedures)} procedures saved")

    print("[7/7] Generating medications...")
    medications = generate_medications(encounters)
    medications.to_csv(DATA_RAW / "medications.csv", index=False)
    print(f"       → {len(medications)} medications saved")

    print("\n✓ All synthetic data saved to:", DATA_RAW)
    print("=" * 60)


if __name__ == "__main__":
    main()
