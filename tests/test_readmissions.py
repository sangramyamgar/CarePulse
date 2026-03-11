"""
Tests for readmission logic.
"""

import pandas as pd
import numpy as np
from datetime import datetime


def test_readmission_flag_with_shift():
    """
    Test the core readmission detection logic using pandas shift(),
    which mirrors how transform.py works.
    """
    # Create sample inpatient encounters for 2 patients
    data = pd.DataFrame({
        "patient_id": ["A", "A", "A", "B", "B"],
        "start_date": pd.to_datetime([
            "2024-01-01", "2024-01-20", "2024-06-01",
            "2024-03-01", "2024-03-25",
        ]),
        "end_date": pd.to_datetime([
            "2024-01-03", "2024-01-22", "2024-06-05",
            "2024-03-04", "2024-03-28",
        ]),
    })

    # Sort by patient and date
    data = data.sort_values(["patient_id", "start_date"])

    # Find next admission per patient
    data["next_admit"] = data.groupby("patient_id")["start_date"].shift(-1)
    data["days_to_readmit"] = (data["next_admit"] - data["end_date"]).dt.days
    data["is_readmit"] = data["days_to_readmit"].notna() & (data["days_to_readmit"] <= 30)

    # Patient A: 
    #   Enc 1 → Enc 2: discharged Jan 3, readmitted Jan 20 = 17 days → READMIT
    #   Enc 2 → Enc 3: discharged Jan 22, next June 1 = 131 days → NOT readmit
    #   Enc 3: last encounter → NOT readmit (no next)
    # Patient B:
    #   Enc 1 → Enc 2: discharged Mar 4, readmitted Mar 25 = 21 days → READMIT
    #   Enc 2: last → NOT readmit

    readmits = data[data["is_readmit"]].reset_index(drop=True)
    assert len(readmits) == 2
    assert readmits.iloc[0]["patient_id"] == "A"
    assert readmits.iloc[0]["days_to_readmit"] == 17
    assert readmits.iloc[1]["patient_id"] == "B"
    assert readmits.iloc[1]["days_to_readmit"] == 21


def test_no_readmission_when_large_gap():
    """No readmission if all encounters are months apart."""
    data = pd.DataFrame({
        "patient_id": ["X", "X"],
        "start_date": pd.to_datetime(["2024-01-01", "2024-07-01"]),
        "end_date": pd.to_datetime(["2024-01-05", "2024-07-08"]),
    })

    data = data.sort_values(["patient_id", "start_date"])
    data["next_admit"] = data.groupby("patient_id")["start_date"].shift(-1)
    data["days_to_readmit"] = (data["next_admit"] - data["end_date"]).dt.days
    data["is_readmit"] = data["days_to_readmit"].notna() & (data["days_to_readmit"] <= 30)

    assert data["is_readmit"].sum() == 0


def test_single_encounter_no_readmission():
    """A patient with only one encounter cannot be readmitted."""
    data = pd.DataFrame({
        "patient_id": ["Z"],
        "start_date": pd.to_datetime(["2024-05-01"]),
        "end_date": pd.to_datetime(["2024-05-03"]),
    })

    data["next_admit"] = data.groupby("patient_id")["start_date"].shift(-1)
    data["days_to_readmit"] = (data["next_admit"] - data["end_date"]).dt.days
    data["is_readmit"] = data["days_to_readmit"].notna() & (data["days_to_readmit"] <= 30)

    assert data["is_readmit"].sum() == 0
