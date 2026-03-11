"""
Data cleaning and validation.

After raw data is loaded into PostgreSQL, this module:
  - Removes exact duplicate rows
  - Standardizes date columns
  - Handles known null patterns
  - Logs data-quality findings
"""

import pandas as pd
from src.db import engine, execute, run_query


def remove_duplicates():
    """Remove exact duplicate rows from key tables."""
    # For tables without a natural PK constraint enforced at insert,
    # we deduplicate in-place using ctid (PostgreSQL row identifier).

    tables_with_pk = ["patients", "encounters", "providers", "organizations"]
    # These tables have a PK column 'id' — duplicates would violate PK.
    # The child tables (conditions, procedures, medications) may have dupes.

    child_tables = [
        ("conditions", ["patient_id", "encounter_id", "code"]),
        ("procedures", ["patient_id", "encounter_id", "code"]),
        ("medications", ["patient_id", "encounter_id", "code"]),
    ]

    for table, key_cols in child_tables:
        key_str = ", ".join(key_cols)
        sql = f"""
        DELETE FROM {table}
        WHERE ctid NOT IN (
            SELECT MIN(ctid)
            FROM {table}
            GROUP BY {key_str}
        );
        """
        execute(sql)
        print(f"  ✓ Deduplicated {table} on ({key_str})")


def validate_dates():
    """Check for encounters where end_date < start_date and fix them."""
    bad_rows = run_query("""
        SELECT id, start_date, end_date
        FROM encounters
        WHERE end_date < start_date
    """)

    if len(bad_rows) > 0:
        print(f"  ⚠ Found {len(bad_rows)} encounters with end_date < start_date — swapping")
        execute("""
            UPDATE encounters
            SET start_date = end_date, end_date = start_date
            WHERE end_date < start_date
        """)
    else:
        print("  ✓ All encounter dates valid")


def validate_not_null():
    """Report null counts for critical columns."""
    checks = [
        ("patients", "birth_date"),
        ("patients", "gender"),
        ("encounters", "patient_id"),
        ("encounters", "start_date"),
        ("encounters", "encounter_class"),
    ]

    for table, col in checks:
        result = run_query(
            f"SELECT COUNT(*) AS null_count FROM {table} WHERE {col} IS NULL"
        )
        null_count = result["null_count"].iloc[0]
        status = "✓" if null_count == 0 else "⚠"
        print(f"  {status} {table}.{col}: {null_count} nulls")


def run_cleaning():
    """Run all cleaning and validation steps."""
    print("\n--- Data Cleaning & Validation ---")

    print("\nStep 1: Remove duplicates")
    remove_duplicates()

    print("\nStep 2: Validate dates")
    validate_dates()

    print("\nStep 3: Check required columns")
    validate_not_null()

    print("\n--- Cleaning complete ---\n")


if __name__ == "__main__":
    run_cleaning()
