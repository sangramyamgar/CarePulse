"""
Utilization analytics.

Functions for encounter volume, length of stay, cost trends,
and service-line breakdowns.
"""

import datetime
import pandas as pd
from src.db import run_query, run_sql_file, date_clause
from src.config import SQL_DIR


def get_headline_metrics(start: datetime.date | None = None, end: datetime.date | None = None) -> dict:
    dc, dp = date_clause(start, end, "start_date", "WHERE" if True else "AND")
    # When no filter, WHERE 1=1 keeps it easy
    where = f"WHERE 1=1 {dc}" if dc else ""
    df = run_query(f"""
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
        {where}
    """, dp)
    return df.iloc[0].to_dict()


def get_monthly_volume(start: datetime.date | None = None, end: datetime.date | None = None) -> pd.DataFrame:
    dc, dp = date_clause(start, end, "start_date", "WHERE")
    where = f"WHERE 1=1 {dc}" if dc else ""
    return run_query(f"""
        SELECT
            DATE_TRUNC('month', start_date)::DATE AS month,
            encounter_class,
            COUNT(*) AS encounter_count
        FROM encounters
        {where}
        GROUP BY 1, 2
        ORDER BY 1, 2
    """, dp)


def get_volume_by_class(start: datetime.date | None = None, end: datetime.date | None = None) -> pd.DataFrame:
    dc, dp = date_clause(start, end, "start_date", "WHERE")
    where = f"WHERE 1=1 {dc}" if dc else ""
    return run_query(f"""
        SELECT
            encounter_class,
            COUNT(*) AS encounter_count,
            ROUND(AVG(total_cost), 2) AS avg_cost,
            ROUND(SUM(total_cost), 2) AS total_cost
        FROM encounters
        {where}
        GROUP BY encounter_class
        ORDER BY encounter_count DESC
    """, dp)


def get_los_by_class(start: datetime.date | None = None, end: datetime.date | None = None) -> pd.DataFrame:
    dc, dp = date_clause(start, end, "start_date", "AND")
    return run_query(f"""
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
          {dc}
        GROUP BY encounter_class
    """, dp)


def get_top_conditions(top_n: int = 10) -> pd.DataFrame:
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


def get_payer_mix(start: datetime.date | None = None, end: datetime.date | None = None) -> pd.DataFrame:
    dc, dp = date_clause(start, end, "start_date", "WHERE")
    where = f"WHERE 1=1 {dc}" if dc else ""
    return run_query(f"""
        SELECT
            payer,
            COUNT(*) AS encounter_count,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
        FROM encounters
        {where}
        GROUP BY payer
        ORDER BY encounter_count DESC
    """, dp)


def get_cost_by_month(start: datetime.date | None = None, end: datetime.date | None = None) -> pd.DataFrame:
    dc, dp = date_clause(start, end, "start_date", "WHERE")
    where = f"WHERE 1=1 {dc}" if dc else ""
    return run_query(f"""
        SELECT
            DATE_TRUNC('month', start_date)::DATE AS month,
            ROUND(SUM(total_cost), 2) AS total_cost,
            ROUND(AVG(total_cost), 2) AS avg_cost,
            COUNT(*) AS encounters
        FROM encounters
        {where}
        GROUP BY 1
        ORDER BY 1
    """, dp)
