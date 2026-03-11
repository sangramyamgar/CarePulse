"""
HEDIS-style quality measure analytics.

Provides functions to compute NCQA-aligned measures (simplified for synthetic data):
  - ACR: All-Cause Readmissions
  - FUH: Follow-Up After Hospitalization for Mental Illness
"""

import pandas as pd
from src.db import run_query, run_sql_file
from src.config import SQL_DIR


# ---------------------------------------------------------------------------
# ACR — All-Cause Readmissions
# ---------------------------------------------------------------------------

def get_acr_summary() -> dict:
    """Return denominator, numerator, and ACR rate from the ACR SQL."""
    df = run_sql_file(str(SQL_DIR / "hedis_acr.sql"))
    if df.empty:
        return {"denominator": 0, "numerator": 0, "acr_rate_pct": 0.0}
    return df.iloc[0].to_dict()


def get_acr_trend() -> pd.DataFrame:
    """ACR rate broken out by discharge quarter."""
    return run_query("""
        WITH index_stays AS (
            SELECT
                e.id AS encounter_id,
                e.patient_id,
                e.end_date AS discharge_date,
                DATE_TRUNC('quarter', e.end_date)::DATE AS quarter,
                EXTRACT(YEAR FROM AGE(e.start_date, p.birth_date))::INTEGER AS age
            FROM encounters e
            JOIN patients p ON e.patient_id = p.id
            WHERE e.encounter_class = 'inpatient'
              AND e.end_date IS NOT NULL
              AND EXTRACT(YEAR FROM AGE(e.start_date, p.birth_date))::INTEGER BETWEEN 18 AND 64
              AND (p.death_date IS NULL OR p.death_date > e.end_date)
        ),
        with_next AS (
            SELECT
                i.*,
                LEAD(i.discharge_date) OVER (
                    PARTITION BY i.patient_id ORDER BY i.discharge_date
                ) AS next_discharge,
                EXTRACT(DAY FROM (
                    LEAD(i.discharge_date) OVER (
                        PARTITION BY i.patient_id ORDER BY i.discharge_date
                    ) - i.discharge_date
                ))::INTEGER AS days_gap
            FROM index_stays i
        )
        SELECT
            quarter,
            COUNT(*) AS denominator,
            SUM(CASE WHEN days_gap IS NOT NULL AND days_gap <= 30
                THEN 1 ELSE 0 END) AS numerator,
            ROUND(100.0 * SUM(CASE WHEN days_gap IS NOT NULL AND days_gap <= 30
                THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS acr_rate_pct
        FROM with_next
        GROUP BY quarter
        ORDER BY quarter
    """)


def get_acr_by_payer() -> pd.DataFrame:
    """ACR rate stratified by payer."""
    return run_query("""
        WITH index_stays AS (
            SELECT
                e.id AS encounter_id,
                e.patient_id,
                e.end_date AS discharge_date,
                e.payer,
                EXTRACT(YEAR FROM AGE(e.start_date, p.birth_date))::INTEGER AS age
            FROM encounters e
            JOIN patients p ON e.patient_id = p.id
            WHERE e.encounter_class = 'inpatient'
              AND e.end_date IS NOT NULL
              AND EXTRACT(YEAR FROM AGE(e.start_date, p.birth_date))::INTEGER BETWEEN 18 AND 64
              AND (p.death_date IS NULL OR p.death_date > e.end_date)
        ),
        with_next AS (
            SELECT
                i.*,
                EXTRACT(DAY FROM (
                    LEAD(i.discharge_date) OVER (
                        PARTITION BY i.patient_id ORDER BY i.discharge_date
                    ) - i.discharge_date
                ))::INTEGER AS days_gap
            FROM index_stays i
        )
        SELECT
            payer,
            COUNT(*) AS denominator,
            SUM(CASE WHEN days_gap <= 30 THEN 1 ELSE 0 END) AS numerator,
            ROUND(100.0 * SUM(CASE WHEN days_gap <= 30 THEN 1 ELSE 0 END)
                  / NULLIF(COUNT(*), 0), 2) AS acr_rate_pct
        FROM with_next
        GROUP BY payer
        ORDER BY acr_rate_pct DESC
    """)


# ---------------------------------------------------------------------------
# FUH — Follow-Up After Hospitalization for Mental Illness
# ---------------------------------------------------------------------------

def get_fuh_summary() -> dict:
    """Return FUH-7 and FUH-30 rates from the FUH SQL."""
    df = run_sql_file(str(SQL_DIR / "hedis_fuh.sql"))
    if df.empty:
        return {
            "denominator": 0,
            "numerator_7d": 0,
            "fuh_7d_rate_pct": 0.0,
            "numerator_30d": 0,
            "fuh_30d_rate_pct": 0.0,
        }
    return df.iloc[0].to_dict()


def get_fuh_by_payer() -> pd.DataFrame:
    """FUH-7 and FUH-30 rates stratified by payer."""
    return run_query("""
        WITH mh_encounters AS (
            SELECT DISTINCT
                e.id AS encounter_id,
                e.patient_id,
                e.end_date AS discharge_date,
                e.payer
            FROM encounters e
            JOIN conditions c ON e.id = c.encounter_id
            WHERE e.encounter_class = 'inpatient'
              AND e.end_date IS NOT NULL
              AND (
                  LOWER(c.description) LIKE '%%depressive%%'
                  OR LOWER(c.description) LIKE '%%anxiety%%'
                  OR LOWER(c.description) LIKE '%%bipolar%%'
                  OR LOWER(c.description) LIKE '%%schizophreni%%'
                  OR LOWER(c.description) LIKE '%%psycho%%'
                  OR LOWER(c.description) LIKE '%%mental%%'
                  OR LOWER(c.description) LIKE '%%stress%%disorder%%'
              )
        ),
        followups AS (
            SELECT
                mh.encounter_id,
                mh.patient_id,
                mh.discharge_date,
                mh.payer,
                MIN(CASE WHEN fu.encounter_class IN ('outpatient','ambulatory')
                          AND fu.start_date > mh.discharge_date
                          AND fu.start_date <= mh.discharge_date + INTERVAL '7 days'
                    THEN fu.start_date END) AS followup_7d,
                MIN(CASE WHEN fu.encounter_class IN ('outpatient','ambulatory')
                          AND fu.start_date > mh.discharge_date
                          AND fu.start_date <= mh.discharge_date + INTERVAL '30 days'
                    THEN fu.start_date END) AS followup_30d
            FROM mh_encounters mh
            LEFT JOIN encounters fu ON mh.patient_id = fu.patient_id
            GROUP BY mh.encounter_id, mh.patient_id, mh.discharge_date, mh.payer
        )
        SELECT
            payer,
            COUNT(*) AS denominator,
            SUM(CASE WHEN followup_7d IS NOT NULL THEN 1 ELSE 0 END) AS numerator_7d,
            ROUND(100.0 * SUM(CASE WHEN followup_7d IS NOT NULL THEN 1 ELSE 0 END)
                  / NULLIF(COUNT(*), 0), 2) AS fuh_7d_rate_pct,
            SUM(CASE WHEN followup_30d IS NOT NULL THEN 1 ELSE 0 END) AS numerator_30d,
            ROUND(100.0 * SUM(CASE WHEN followup_30d IS NOT NULL THEN 1 ELSE 0 END)
                  / NULLIF(COUNT(*), 0), 2) AS fuh_30d_rate_pct
        FROM followups
        GROUP BY payer
        ORDER BY fuh_30d_rate_pct DESC
    """)
