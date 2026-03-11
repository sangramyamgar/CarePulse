"""
Build derived/analytic tables from the base data.

Main output: the `readmissions` table, which powers most dashboard analytics.
"""

import pandas as pd
import numpy as np
from src.db import engine, run_query, execute
from src.config import AGE_BINS, AGE_LABELS, READMISSION_WINDOW_DAYS


def build_readmissions_table():
    """
    Build the readmissions analytic table.

    Logic:
      1. Pull all inpatient encounters
      2. For each patient, find the next inpatient admission after each discharge
      3. Calculate days_to_readmit
      4. Flag 30-day readmissions
      5. Enrich with age group, primary condition, chronic condition count
      6. Write to the readmissions table
    """

    print("  Building readmissions table...")

    # Step 1: Get inpatient encounters with patient birth dates
    encounters = run_query("""
        SELECT
            e.id AS encounter_id,
            e.patient_id,
            e.start_date,
            e.end_date AS discharge_date,
            e.encounter_class,
            e.payer,
            e.org_id,
            p.birth_date
        FROM encounters e
        JOIN patients p ON e.patient_id = p.id
        WHERE e.encounter_class = 'inpatient'
          AND e.end_date IS NOT NULL
        ORDER BY e.patient_id, e.start_date
    """)

    if encounters.empty:
        print("  ⚠ No inpatient encounters found")
        return

    # Step 2: Calculate next admission date per patient using shift
    encounters["start_date"] = pd.to_datetime(encounters["start_date"])
    encounters["discharge_date"] = pd.to_datetime(encounters["discharge_date"])
    encounters["birth_date"] = pd.to_datetime(encounters["birth_date"])

    encounters = encounters.sort_values(["patient_id", "start_date"])
    encounters["next_admit_date"] = encounters.groupby("patient_id")["start_date"].shift(-1)

    # Step 3: Calculate days to readmit
    encounters["days_to_readmit"] = (
        encounters["next_admit_date"] - encounters["discharge_date"]
    ).dt.days

    # Step 4: Flag 30-day readmissions
    encounters["is_30day_readmit"] = (
        encounters["days_to_readmit"].notna()
        & (encounters["days_to_readmit"] <= READMISSION_WINDOW_DAYS)
        & (encounters["days_to_readmit"] >= 0)
    )

    # Step 5: Calculate age at encounter
    encounters["age_at_encounter"] = (
        (encounters["start_date"] - encounters["birth_date"]).dt.days // 365
    )

    # Assign age group
    encounters["age_group"] = pd.cut(
        encounters["age_at_encounter"],
        bins=AGE_BINS,
        labels=AGE_LABELS,
        right=False,
    )

    # Step 6: Get primary condition and chronic count per encounter
    conditions = run_query("""
        SELECT encounter_id, description, code
        FROM conditions
    """)

    # Primary condition = first condition listed for the encounter
    primary = (
        conditions.groupby("encounter_id")["description"]
        .first()
        .reset_index()
        .rename(columns={"description": "primary_condition"})
    )

    # Chronic condition count = distinct chronic conditions per patient
    # We define "chronic" as conditions that appear in our CHRONIC list
    # (simplified: conditions where resolved_date is NULL)
    chronic_counts = run_query("""
        SELECT
            c.patient_id,
            COUNT(DISTINCT c.code) AS chronic_count
        FROM conditions c
        WHERE c.resolved_date IS NULL
        GROUP BY c.patient_id
    """)

    # Merge enrichments
    encounters = encounters.merge(primary, left_on="encounter_id",
                                  right_on="encounter_id", how="left")
    encounters = encounters.merge(chronic_counts, on="patient_id", how="left")
    encounters["chronic_count"] = encounters["chronic_count"].fillna(0).astype(int)

    # Step 7: Select final columns and write to DB
    readmissions = encounters[[
        "encounter_id", "patient_id", "discharge_date", "next_admit_date",
        "days_to_readmit", "is_30day_readmit", "age_at_encounter", "age_group",
        "primary_condition", "chronic_count", "encounter_class", "payer", "org_id",
    ]].copy()

    # Drop existing readmissions table data and reload
    execute("DELETE FROM readmissions")
    readmissions.to_sql("readmissions", engine, if_exists="append", index=False)

    total = len(readmissions)
    readmits = readmissions["is_30day_readmit"].sum()
    rate = round(100 * readmits / total, 1) if total > 0 else 0
    print(f"  ✓ Readmissions table: {total:,} rows, {readmits:,} 30-day readmissions ({rate}%)")


def run_transforms():
    """Run all transformation steps."""
    print("\n--- Building Derived Tables ---")
    build_readmissions_table()
    print("--- Transforms complete ---\n")


if __name__ == "__main__":
    run_transforms()
