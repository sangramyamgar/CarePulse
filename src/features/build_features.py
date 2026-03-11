"""
Build feature table for optional risk scoring model.

Creates a patient-encounter-level feature set suitable for
logistic regression (readmission risk prediction).
"""

import pandas as pd
import numpy as np
from src.db import run_query


def build_readmission_features() -> pd.DataFrame:
    """
    Build a flat feature table for readmission risk scoring.

    Each row = one inpatient encounter. Target = is_30day_readmit.

    Features:
      - age_at_encounter
      - gender (binary: 1 = M)
      - chronic_count (number of active chronic conditions)
      - los_days (length of stay)
      - total_cost
      - encounter_month
      - is_emergency_prior_30d (had an ED visit in 30 days before this admission)
      - prior_inpatient_count (inpatient visits in the prior 12 months)
    """

    df = run_query("""
        WITH base AS (
            SELECT
                r.encounter_id,
                r.patient_id,
                r.is_30day_readmit,
                r.age_at_encounter,
                r.chronic_count,
                r.payer,
                p.gender,
                e.start_date,
                e.end_date,
                e.total_cost,
                EXTRACT(DAY FROM (e.end_date - e.start_date)) AS los_days,
                EXTRACT(MONTH FROM e.start_date) AS encounter_month
            FROM readmissions r
            JOIN encounters e ON r.encounter_id = e.id
            JOIN patients p ON r.patient_id = p.id
        ),
        -- Count prior inpatient encounters in the last 12 months
        prior_visits AS (
            SELECT
                b.encounter_id,
                COUNT(e2.id) AS prior_inpatient_count
            FROM base b
            LEFT JOIN encounters e2
                ON e2.patient_id = b.patient_id
                AND e2.encounter_class = 'inpatient'
                AND e2.start_date < b.start_date
                AND e2.start_date >= b.start_date - INTERVAL '365 days'
            GROUP BY b.encounter_id
        ),
        -- Check for ED visit in 30 days before admission
        prior_ed AS (
            SELECT
                b.encounter_id,
                CASE WHEN COUNT(e3.id) > 0 THEN 1 ELSE 0 END AS is_emergency_prior_30d
            FROM base b
            LEFT JOIN encounters e3
                ON e3.patient_id = b.patient_id
                AND e3.encounter_class = 'emergency'
                AND e3.start_date < b.start_date
                AND e3.start_date >= b.start_date - INTERVAL '30 days'
            GROUP BY b.encounter_id
        )
        SELECT
            b.*,
            pv.prior_inpatient_count,
            pe.is_emergency_prior_30d
        FROM base b
        LEFT JOIN prior_visits pv ON b.encounter_id = pv.encounter_id
        LEFT JOIN prior_ed pe ON b.encounter_id = pe.encounter_id
    """)

    # Encode gender as binary
    df["is_male"] = (df["gender"] == "M").astype(int)

    # Fill nulls
    df["los_days"] = df["los_days"].fillna(0)
    df["total_cost"] = df["total_cost"].fillna(0)
    df["chronic_count"] = df["chronic_count"].fillna(0)
    df["prior_inpatient_count"] = df["prior_inpatient_count"].fillna(0)
    df["is_emergency_prior_30d"] = df["is_emergency_prior_30d"].fillna(0)

    return df
