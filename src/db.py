"""
Database connection helper.
Provides a SQLAlchemy engine and a convenience function to run queries.
"""

import pandas as pd
from sqlalchemy import create_engine, text
from src.config import DATABASE_URL

# Create a single reusable engine
engine = create_engine(DATABASE_URL, echo=False)


def run_query(sql: str, params: dict | None = None) -> pd.DataFrame:
    """Execute a SQL query and return a DataFrame."""
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


def run_sql_file(filepath: str, params: dict | None = None) -> pd.DataFrame:
    """Read a .sql file and execute it, returning a DataFrame."""
    with open(filepath) as f:
        sql = f.read()
    return run_query(sql, params)


def execute(sql: str, params: dict | None = None):
    """Execute a SQL statement (INSERT, CREATE, etc.) without returning rows."""
    with engine.begin() as conn:
        conn.execute(text(sql), params or {})
