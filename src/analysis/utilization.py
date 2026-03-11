"""
Utilization analytics.

Functions for encounter volume, length of stay, cost trends,
and service-line breakdowns.
"""

import pandas as pd
from src.db import run_query, run_sql_file
from src.config import SQL_DIR


def get_headline_metrics() -> dict:
    """Key utilization numbers for the executive overview."""
    df = run_query("""
        SELECT
            COUNT(*)                                                AS total_encounters,
            COUNT(DISTINCT patient_id)                              AS total_patients,
            COUNT(DISTINCT org_id)                                  AS total_facilities,
            ROUND(AVG(total_cost), 2)                               AS avg_cost,
            ROUND(SUM(total_cost), 2)                               AS total_cost,
            ROUND(AVG(
                CASE WHEN encounter_class = 'inpatient'
                     THEN EXTRACT(DAY FROM (end_date - start_date))
                END
            ), 1) AS avg_los_days
        FROM encounters
    """)
    return df.iloc[0].to_dict()


def get_monthly_volume() -> pd.DataFrame:
    """Monthly encounter volume by encounter class."""
    return run_sql_file(str(SQL_DIR / "utilization_metrics.sql"))


def get_volume_by_class() -> pd.DataFrame:
    """Total encounters by class."""
    return run_query("""
        SELECT
            encounter_class,
            COUNT(*) AS encounter_count,
            ROUND(AVG(total_cost), 2) AS avg_cost,
            ROUND(SUM(total_cost), 2) AS total_cost
        FROM encounters
        GROUP BY encounter_class
        ORDER BY encounter_count DESC
    """)


def get_los_by_class() -> pd.DataFrame:
    """Average length of stay by encounter class (inpatient & emergency)."""
    return run_query("""
        SELECT
            encounter_class,
            COUNT(*) AS encounters,
            ROUND(AVG(EXTRACT(DAY FROM (end_date - start_date))), 1) AS avg_los,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (
                ORDER BY EXTRACT(DAY FROM (end_date - start_date))
            ), 1) AS median_los
        FROM encounters
        WHERE encounter_class IN ('inpatient', 'emergency')
          AND end_date IS NOT NULL
        GROUP BY encounter_class
    """)


def get_top_conditions(top_n: int = 10) -> pd.DataFrame:
    """Most frequent conditions across all encounters."""
    return run_query(f"""
        SELECT
            c.description AS condition,
            COUNT(*) AS frequency,
            COUNT(DISTINCT c.patient_id) AS unique_patients
        FROM conditions c
        GROUP BY c.description
        ORDER BY frequency DESC
        LIMIT {int(top_n)}
    """)


def get_payer_mix() -> pd.DataFrame:
    """Encounter distribution by payer."""
    return run_query("""
        SELECT
            payer,
            COUNT(*) AS encounter_count,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
        FROM encounters
        GROUP BY payer
        ORDER BY encounter_count DESC
    """)


def get_cost_by_month() -> pd.DataFrame:
    """Monthly total and average cost trend."""
    return run_query("""
        SELECT
            DATE_TRUNC('month', start_date)::DATE AS month,
            ROUND(SUM(total_cost), 2) AS total_cost,
            ROUND(AVG(total_cost), 2) AS avg_cost,
            COUNT(*) AS encounters
        FROM encounters
        GROUP BY 1
        ORDER BY 1
    """)
