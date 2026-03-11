"""
Data quality checks and monitoring.

Functions that assess completeness, validity, and freshness of the data.
Used by the Data Quality dashboard page.
"""

import pandas as pd
from src.db import run_query, run_sql_file
from src.config import SQL_DIR


def get_table_row_counts() -> pd.DataFrame:
    """Row counts for every table in the schema."""
    return run_sql_file(str(SQL_DIR / "data_quality.sql"))


def get_column_completeness() -> pd.DataFrame:
    """Null percentage for important columns across all tables."""
    checks = [
        ("patients", "id"), ("patients", "birth_date"), ("patients", "gender"),
        ("patients", "race"), ("patients", "zip"),
        ("encounters", "id"), ("encounters", "patient_id"),
        ("encounters", "start_date"), ("encounters", "end_date"),
        ("encounters", "encounter_class"), ("encounters", "total_cost"),
        ("encounters", "payer"), ("encounters", "org_id"),
        ("conditions", "description"), ("conditions", "code"),
        ("providers", "specialty"),
        ("readmissions", "primary_condition"), ("readmissions", "age_group"),
    ]

    results = []
    for table, col in checks:
        df = run_query(f"""
            SELECT
                '{table}' AS table_name,
                '{col}' AS column_name,
                COUNT(*) AS total_rows,
                SUM(CASE WHEN {col} IS NULL THEN 1 ELSE 0 END) AS null_count,
                ROUND(
                    100.0 * SUM(CASE WHEN {col} IS NULL THEN 1 ELSE 0 END)
                    / NULLIF(COUNT(*), 0), 1
                ) AS null_pct
            FROM {table}
        """)
        results.append(df)

    return pd.concat(results, ignore_index=True)


def get_encounter_date_range() -> dict:
    """Earliest and latest encounter dates — useful for freshness check."""
    df = run_query("""
        SELECT
            MIN(start_date)::DATE AS earliest,
            MAX(start_date)::DATE AS latest,
            COUNT(DISTINCT DATE_TRUNC('month', start_date)) AS months_covered
        FROM encounters
    """)
    return df.iloc[0].to_dict()


def get_duplicate_check() -> pd.DataFrame:
    """Check for potential duplicates in key tables."""
    tables = {
        "patients": "id",
        "encounters": "id",
        "providers": "id",
        "organizations": "id",
    }

    results = []
    for table, pk in tables.items():
        df = run_query(f"""
            SELECT
                '{table}' AS table_name,
                COUNT(*) AS total_rows,
                COUNT(DISTINCT {pk}) AS distinct_keys,
                COUNT(*) - COUNT(DISTINCT {pk}) AS duplicate_count
            FROM {table}
        """)
        results.append(df)

    return pd.concat(results, ignore_index=True)


def get_orphan_records() -> pd.DataFrame:
    """Find records referencing non-existent parent keys."""
    checks = [
        ("encounters with missing patient",
         "SELECT COUNT(*) AS orphan_count FROM encounters e "
         "LEFT JOIN patients p ON e.patient_id = p.id WHERE p.id IS NULL"),
        ("conditions with missing encounter",
         "SELECT COUNT(*) AS orphan_count FROM conditions c "
         "LEFT JOIN encounters e ON c.encounter_id = e.id WHERE e.id IS NULL"),
        ("encounters with missing org",
         "SELECT COUNT(*) AS orphan_count FROM encounters e "
         "LEFT JOIN organizations o ON e.org_id = o.id WHERE o.id IS NULL"),
    ]

    results = []
    for label, sql in checks:
        df = run_query(sql)
        df["check_name"] = label
        results.append(df)

    return pd.concat(results, ignore_index=True)[["check_name", "orphan_count"]]


def get_data_quality_score() -> float:
    """
    Overall data quality score (0-100).

    Computed as average of:
      - Completeness: % of non-null values across key columns
      - Uniqueness: % of tables with 0 duplicates
      - Referential integrity: % of checks with 0 orphans
    """
    # Completeness
    comp = get_column_completeness()
    completeness = 100 - comp["null_pct"].mean() if not comp.empty else 100

    # Uniqueness
    dupes = get_duplicate_check()
    uniqueness = (
        100 * (dupes["duplicate_count"] == 0).sum() / len(dupes)
        if not dupes.empty else 100
    )

    # Referential integrity
    orphans = get_orphan_records()
    integrity = (
        100 * (orphans["orphan_count"] == 0).sum() / len(orphans)
        if not orphans.empty else 100
    )

    return round((completeness + uniqueness + integrity) / 3, 1)
