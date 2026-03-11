"""
Facility and provider analytics.

Functions for facility comparisons and provider drilldowns.
"""

import pandas as pd
from src.db import run_query, run_sql_file
from src.config import SQL_DIR


def get_facility_comparison() -> pd.DataFrame:
    """Comprehensive facility comparison with key metrics."""
    return run_sql_file(str(SQL_DIR / "facility_comparison.sql"))


def get_facility_monthly_volume(facility_name: str | None = None) -> pd.DataFrame:
    """Monthly encounter volume for a specific facility or all facilities."""
    where = ""
    params = {}
    if facility_name:
        where = "WHERE o.name = :facility_name"
        params = {"facility_name": facility_name}

    return run_query(f"""
        SELECT
            o.name AS facility_name,
            DATE_TRUNC('month', e.start_date)::DATE AS month,
            e.encounter_class,
            COUNT(*) AS encounter_count
        FROM encounters e
        JOIN organizations o ON e.org_id = o.id
        {where}
        GROUP BY 1, 2, 3
        ORDER BY 1, 2, 3
    """, params)


def get_provider_summary() -> pd.DataFrame:
    """Provider-level summary: encounter count, avg cost, specialties."""
    return run_query("""
        SELECT
            prov.name AS provider_name,
            prov.specialty,
            o.name AS facility_name,
            COUNT(e.id) AS encounter_count,
            COUNT(DISTINCT e.patient_id) AS unique_patients,
            ROUND(AVG(e.total_cost), 2) AS avg_cost
        FROM encounters e
        JOIN providers prov ON e.provider_id = prov.id
        JOIN organizations o ON prov.org_id = o.id
        GROUP BY prov.name, prov.specialty, o.name
        ORDER BY encounter_count DESC
    """)


def get_facility_readmission_comparison() -> pd.DataFrame:
    """Readmission rates by facility."""
    return run_query("""
        SELECT
            o.name AS facility_name,
            COUNT(r.encounter_id) AS inpatient_encounters,
            SUM(CASE WHEN r.is_30day_readmit THEN 1 ELSE 0 END) AS readmissions,
            ROUND(
                100.0 * SUM(CASE WHEN r.is_30day_readmit THEN 1 ELSE 0 END)
                / NULLIF(COUNT(r.encounter_id), 0), 1
            ) AS readmission_rate
        FROM readmissions r
        JOIN organizations o ON r.org_id = o.id
        GROUP BY o.name
        ORDER BY readmission_rate DESC
    """)
