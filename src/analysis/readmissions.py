"""
Readmission analytics.

Functions that query the readmissions table and return DataFrames
ready for dashboard consumption.
"""

import datetime
import pandas as pd
from src.db import run_query, run_sql_file, date_clause
from src.config import SQL_DIR


def get_overall_readmission_rate(start: datetime.date | None = None, end: datetime.date | None = None) -> dict:
    dc, dp = date_clause(start, end, "discharge_date", "WHERE")
    where = f"WHERE 1=1 {dc}" if dc else ""
    df = run_query(f"""
        SELECT
            COUNT(*) AS total_inpatient,
            SUM(CASE WHEN is_30day_readmit THEN 1 ELSE 0 END) AS readmissions,
            ROUND(
                100.0 * SUM(CASE WHEN is_30day_readmit THEN 1 ELSE 0 END)
                / NULLIF(COUNT(*), 0), 1
            ) AS readmission_rate
        FROM readmissions
        {where}
    """, dp)
    return df.iloc[0].to_dict()


def get_readmission_trend(start: datetime.date | None = None, end: datetime.date | None = None) -> pd.DataFrame:
    dc, dp = date_clause(start, end, "discharge_date", "WHERE")
    where = f"WHERE 1=1 {dc}" if dc else ""
    return run_query(f"""
        SELECT
            DATE_TRUNC('month', discharge_date)::DATE AS month,
            COUNT(*) AS total_discharges,
            SUM(CASE WHEN is_30day_readmit THEN 1 ELSE 0 END) AS readmissions,
            ROUND(
                100.0 * SUM(CASE WHEN is_30day_readmit THEN 1 ELSE 0 END)
                / NULLIF(COUNT(*), 0), 1
            ) AS readmission_rate
        FROM readmissions
        {where}
        GROUP BY 1
        ORDER BY 1
    """, dp)


def get_readmission_by_age_group() -> pd.DataFrame:
    return run_sql_file(str(SQL_DIR / "cohort_analysis.sql"))


def get_readmission_by_condition(top_n: int = 10) -> pd.DataFrame:
    return run_query(f"""
        SELECT
            primary_condition,
            COUNT(*) AS total_encounters,
            SUM(CASE WHEN is_30day_readmit THEN 1 ELSE 0 END) AS readmissions,
            ROUND(
                100.0 * SUM(CASE WHEN is_30day_readmit THEN 1 ELSE 0 END)
                / NULLIF(COUNT(*), 0), 1
            ) AS readmission_rate
        FROM readmissions
        WHERE primary_condition IS NOT NULL
        GROUP BY primary_condition
        ORDER BY total_encounters DESC
        LIMIT {int(top_n)}
    """)


def get_readmission_by_payer() -> pd.DataFrame:
    return run_query("""
        SELECT
            payer,
            COUNT(*) AS total_encounters,
            SUM(CASE WHEN is_30day_readmit THEN 1 ELSE 0 END) AS readmissions,
            ROUND(
                100.0 * SUM(CASE WHEN is_30day_readmit THEN 1 ELSE 0 END)
                / NULLIF(COUNT(*), 0), 1
            ) AS readmission_rate
        FROM readmissions
        GROUP BY payer
        ORDER BY total_encounters DESC
    """)


def get_readmission_by_chronic_count() -> pd.DataFrame:
    return run_query("""
        SELECT
            chronic_count,
            COUNT(*) AS total_encounters,
            SUM(CASE WHEN is_30day_readmit THEN 1 ELSE 0 END) AS readmissions,
            ROUND(
                100.0 * SUM(CASE WHEN is_30day_readmit THEN 1 ELSE 0 END)
                / NULLIF(COUNT(*), 0), 1
            ) AS readmission_rate
        FROM readmissions
        GROUP BY chronic_count
        ORDER BY chronic_count
    """)


def get_days_to_readmit_distribution() -> pd.DataFrame:
    return run_query("""
        SELECT days_to_readmit
        FROM readmissions
        WHERE next_admit_date IS NOT NULL
          AND days_to_readmit >= 0
          AND days_to_readmit <= 90
    """)
