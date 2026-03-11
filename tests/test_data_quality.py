"""
Tests for data quality check logic.
"""

import pandas as pd
import numpy as np


def test_completeness_calculation():
    """Test null percentage calculation."""
    df = pd.DataFrame({
        "a": [1, 2, None, 4, 5],
        "b": [None, None, 3, 4, 5],
    })

    null_pct_a = round(100.0 * df["a"].isna().sum() / len(df), 1)
    null_pct_b = round(100.0 * df["b"].isna().sum() / len(df), 1)

    assert null_pct_a == 20.0
    assert null_pct_b == 40.0


def test_duplicate_detection():
    """Test that duplicates are correctly identified."""
    df = pd.DataFrame({
        "id": ["A", "B", "C", "A", "D"],
        "value": [1, 2, 3, 1, 5],
    })

    total = len(df)
    distinct = df["id"].nunique()
    duplicates = total - distinct

    assert total == 5
    assert distinct == 4
    assert duplicates == 1


def test_no_duplicates():
    """Clean data should show zero duplicates."""
    df = pd.DataFrame({
        "id": ["A", "B", "C", "D"],
    })

    duplicates = len(df) - df["id"].nunique()
    assert duplicates == 0


def test_referential_integrity():
    """Child records should reference existing parent keys."""
    parents = pd.DataFrame({"id": ["P1", "P2", "P3"]})
    children = pd.DataFrame({"parent_id": ["P1", "P2", "P4"]})

    # P4 is an orphan — not in parents
    merged = children.merge(parents, left_on="parent_id", right_on="id", how="left")
    orphans = merged["id"].isna().sum()

    assert orphans == 1


def test_date_validity():
    """End dates should not be before start dates."""
    df = pd.DataFrame({
        "start": pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01"]),
        "end": pd.to_datetime(["2024-01-05", "2024-01-15", "2024-03-10"]),
    })

    # Check: end >= start for all rows
    invalid = (df["end"] < df["start"]).sum()
    assert invalid == 1  # Feb 1 → Jan 15 is invalid


def test_quality_score_calculation():
    """Test the quality score formula."""
    completeness = 95.0
    uniqueness = 100.0
    integrity = 100.0

    score = round((completeness + uniqueness + integrity) / 3, 1)
    assert score == 98.3
