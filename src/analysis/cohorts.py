"""
Cohort analytics.

Functions for age-group, chronic-condition, and demographic breakdowns.
"""

import pandas as pd
from src.db import run_query


def get_patient_demographics() -> pd.DataFrame:
    """Patient count by gender and race."""
    return run_query("""
        SELECT
            gender,
            race,
            COUNT(*) AS patient_count
        FROM patients
        GROUP BY gender, race
        ORDER BY patient_count DESC
    """)


def get_age_distribution() -> pd.DataFrame:
    """Age distribution of current patients."""
    return run_query("""
        SELECT
            CASE
                WHEN age < 18 THEN '0-17'
                WHEN age < 30 THEN '18-29'
                WHEN age < 45 THEN '30-44'
                WHEN age < 60 THEN '45-59'
                WHEN age < 75 THEN '60-74'
                ELSE '75+'
            END AS age_group,
            COUNT(*) AS patient_count
        FROM (
            SELECT
                EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date))::INTEGER AS age
            FROM patients
            WHERE death_date IS NULL
        ) sub
        GROUP BY 1
        ORDER BY 1
    """)


def get_chronic_burden() -> pd.DataFrame:
    """Distribution of patients by number of chronic (unresolved) conditions."""
    return run_query("""
        WITH patient_chronic AS (
            SELECT
                patient_id,
                COUNT(DISTINCT code) AS chronic_count
            FROM conditions
            WHERE resolved_date IS NULL
            GROUP BY patient_id
        )
        SELECT
            chronic_count,
            COUNT(*) AS patient_count
        FROM patient_chronic
        GROUP BY chronic_count
        ORDER BY chronic_count
    """)


def get_multi_condition_patients(min_conditions: int = 3) -> pd.DataFrame:
    """Patients with a high chronic-condition burden."""
    return run_query(f"""
        WITH patient_chronic AS (
            SELECT
                c.patient_id,
                COUNT(DISTINCT c.code) AS chronic_count,
                STRING_AGG(DISTINCT c.description, ', ') AS conditions_list
            FROM conditions c
            WHERE c.resolved_date IS NULL
            GROUP BY c.patient_id
            HAVING COUNT(DISTINCT c.code) >= {int(min_conditions)}
        )
        SELECT
            pc.patient_id,
            p.gender,
            EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.birth_date))::INTEGER AS age,
            pc.chronic_count,
            pc.conditions_list
        FROM patient_chronic pc
        JOIN patients p ON pc.patient_id = p.id
        ORDER BY pc.chronic_count DESC
        LIMIT 100
    """)


def get_encounter_by_age_group() -> pd.DataFrame:
    """Encounter counts by age group and encounter class."""
    return run_query("""
        SELECT
            CASE
                WHEN EXTRACT(YEAR FROM AGE(e.start_date, p.birth_date))::INTEGER < 18 THEN '0-17'
                WHEN EXTRACT(YEAR FROM AGE(e.start_date, p.birth_date))::INTEGER < 30 THEN '18-29'
                WHEN EXTRACT(YEAR FROM AGE(e.start_date, p.birth_date))::INTEGER < 45 THEN '30-44'
                WHEN EXTRACT(YEAR FROM AGE(e.start_date, p.birth_date))::INTEGER < 60 THEN '45-59'
                WHEN EXTRACT(YEAR FROM AGE(e.start_date, p.birth_date))::INTEGER < 75 THEN '60-74'
                ELSE '75+'
            END AS age_group,
            e.encounter_class,
            COUNT(*) AS encounter_count
        FROM encounters e
        JOIN patients p ON e.patient_id = p.id
        GROUP BY 1, 2
        ORDER BY 1, 2
    """)
