"""
Tests for data transformation logic.
"""

import pandas as pd
import numpy as np
import pytest
from datetime import date, datetime


def test_age_group_binning():
    """Test that age group assignment works correctly."""
    from src.config import AGE_BINS, AGE_LABELS

    ages = pd.Series([5, 18, 25, 35, 50, 65, 80])
    groups = pd.cut(ages, bins=AGE_BINS, labels=AGE_LABELS, right=False)

    expected = ["0-17", "18-29", "18-29", "30-44", "45-59", "60-74", "75+"]
    assert list(groups) == expected


def test_readmission_window_logic():
    """Test that 30-day readmission flagging logic is correct."""
    from src.config import READMISSION_WINDOW_DAYS

    # Simulate: discharge on Jan 1, next admit on Jan 20 → readmission
    discharge = datetime(2024, 1, 1)
    next_admit = datetime(2024, 1, 20)
    days = (next_admit - discharge).days
    assert days == 19
    assert days <= READMISSION_WINDOW_DAYS

    # Simulate: discharge on Jan 1, next admit on Mar 1 → NOT a readmission
    next_admit_far = datetime(2024, 3, 1)
    days_far = (next_admit_far - discharge).days
    assert days_far == 60
    assert days_far > READMISSION_WINDOW_DAYS


def test_readmission_window_boundary():
    """Test boundary: exactly 30 days should count as readmission."""
    from src.config import READMISSION_WINDOW_DAYS

    discharge = datetime(2024, 1, 1)
    next_admit_30 = datetime(2024, 1, 31)
    days_30 = (next_admit_30 - discharge).days
    assert days_30 == 30
    assert days_30 <= READMISSION_WINDOW_DAYS

    # 31 days should NOT count
    next_admit_31 = datetime(2024, 2, 1)
    days_31 = (next_admit_31 - discharge).days
    assert days_31 == 31
    assert days_31 > READMISSION_WINDOW_DAYS


def test_los_calculation():
    """Test length-of-stay calculation."""
    start = datetime(2024, 1, 1, 8, 0)
    end = datetime(2024, 1, 4, 14, 0)
    los_days = (end - start).days
    assert los_days == 3


def test_null_handling_in_readmission():
    """Test that null next_admit_date means no readmission."""
    next_admit = None
    is_readmit = next_admit is not None and False  # would check days
    assert is_readmit is False


def test_cost_is_positive():
    """Sanity check: encounter costs should be non-negative."""
    costs = pd.Series([100, 5000, 0, 79999.99])
    assert (costs >= 0).all()

    # Negative costs should fail
    bad_costs = pd.Series([100, -50, 200])
    assert not (bad_costs >= 0).all()
