"""
Load raw CSV files into PostgreSQL.

Reads each CSV from data/raw/ and writes it to the corresponding
PostgreSQL table. The schema must already exist (run sql/schema.sql first).
"""

import pandas as pd
from sqlalchemy import text
from src.config import DATA_RAW
from src.db import engine


# Mapping of CSV filenames to table names (load order matters for FK constraints)
TABLE_LOAD_ORDER = [
    ("organizations.csv", "organizations"),
    ("providers.csv", "providers"),
    ("patients.csv", "patients"),
    ("encounters.csv", "encounters"),
    ("conditions.csv", "conditions"),
    ("procedures.csv", "procedures"),
    ("medications.csv", "medications"),
]


def load_csv_to_table(csv_name: str, table_name: str) -> int:
    """Load a single CSV into a PostgreSQL table. Returns row count."""
    filepath = DATA_RAW / csv_name
    if not filepath.exists():
        print(f"  ⚠ {csv_name} not found — skipping")
        return 0

    df = pd.read_csv(filepath)

    # Truncate first (preserves schema + FK constraints), then append
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))

    df.to_sql(table_name, engine, if_exists="append", index=False, method="multi")

    return len(df)


def load_all():
    """Load all raw CSVs into PostgreSQL in the correct order."""
    print("\n--- Loading raw CSVs into PostgreSQL ---")

    for csv_name, table_name in TABLE_LOAD_ORDER:
        count = load_csv_to_table(csv_name, table_name)
        print(f"  ✓ {table_name}: {count:,} rows loaded")

    print("--- Loading complete ---\n")


if __name__ == "__main__":
    load_all()
