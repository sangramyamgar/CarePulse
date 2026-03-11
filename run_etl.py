"""
CarePulse ETL Pipeline — Single Entry Point

Usage:
    python run_etl.py

This script runs the full pipeline:
  1. Create database schema (tables)
  2. Generate synthetic data (if CSVs don't exist)
  3. Load CSVs into PostgreSQL
  4. Clean and validate data
  5. Build derived tables (readmissions)
"""

import sys
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import DATA_RAW, SQL_DIR
from src.db import execute


def create_schema():
    """Run schema.sql to create/recreate all tables."""
    print("\n--- Creating Database Schema ---")
    schema_path = SQL_DIR / "schema.sql"
    with open(schema_path) as f:
        sql = f.read()
    execute(sql)
    print("  ✓ All tables created")
    print("--- Schema ready ---\n")


def generate_data_if_needed():
    """Generate synthetic CSVs if they don't exist yet."""
    csv_files = list(DATA_RAW.glob("*.csv"))
    if len(csv_files) >= 7:
        print("  ✓ Synthetic data already exists — skipping generation")
        return

    print("  Generating synthetic data...")
    from src.etl.generate_synthetic_data import main as gen_main
    gen_main()


def main():
    print("=" * 60)
    print("  CarePulse — Full ETL Pipeline")
    print("=" * 60)

    # Step 1: Create schema
    create_schema()

    # Step 2: Generate data if needed
    generate_data_if_needed()

    # Step 3: Load raw data
    from src.etl.load_raw import load_all
    load_all()

    # Step 4: Clean and validate
    from src.etl.clean import run_cleaning
    run_cleaning()

    # Step 5: Build derived tables
    from src.etl.transform import run_transforms
    run_transforms()

    print("=" * 60)
    print("  ✓ ETL Pipeline Complete!")
    print("  Next: streamlit run app/Home.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
