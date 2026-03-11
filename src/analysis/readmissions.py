"""
Readmission analytics.

Functions that query the readmissions table and return DataFrames
ready for dashboard consumption.
"""

import pandas as pd
from src.db import run_query, run_sql_file
from src.config import SQL_DIR


def get_overall_readmission_rate() -> dict:
    """Return headline readmission metrics as a dictionary."""
    df = run_query("""
        SELECT
            COUNT(*) AS total_inpatient,
            SUM(CASE WHEN is_30day_readmit THEN 1 ELSE 0 END) AS readmissions,
            ROUND(
                100.0 * SUM(CASE WHEN is_30day_readmit THEN 1 ELSE 0 END)
                / NULLIF(COUNT(*), 0), 1
            ) AS readmission_rate
        FROM readmissions
    """)
    return df.iloc[0].to_dict()


def get_readmission_trend() -> pd.DataFrame:
    """Monthly readmission rate trend."""
    return run_query("""
        SELECT
            DATE_TRUNC('month', discharge_date)::DATE AS month,
            COUNT(*) AS total_discharges,
            SUM(CASE WHEN is_30day_readmit THEN 1 ELSE 0 END) AS readmissions,
            ROUND(
                100.0 * SUM(CASE WHEN is_30day_readmit THEN 1 ELSE 0 END)
                / NULLIF(COUNT(*), 0), 1
            ) AS readmission_rate
        FROM readmissions
        GROUP BY 1
        ORDER BY 1
    """)


def get_readmission_by_age_group() -> pd.DataFrame:
    """Readmission rate broken down by age group."""
    return run_sql_file(str(SQL_DIR / "cohort_analysis.sql"))


def get_readmission_by_condition(top_n: int = 10) -> pd.DataFrame:
    """Readmission rate by primary condition (top N)."""
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
    """Readmission rate by payer."""
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
    """Readmission rate by number of chronic conditions."""
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
    """Distribution of days to readmission (only those who were readmitted)."""
    return run_query("""
        SELECT days_to_readmit
        FROM readmissions
        WHERE next_admit_date IS NOT NULL
          AND days_to_readmit >= 0
          AND days_to_readmit <= 90
    """)
