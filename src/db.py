"""
Database connection helper.

Provides a SQLAlchemy engine (PostgreSQL) with automatic fallback to an
in-memory DuckDB database loaded from CSV files.  The fallback activates
when the DEMO_MODE env-var is set or PostgreSQL is unreachable.
"""

import datetime
import os
import re
from pathlib import Path

import pandas as pd
from src.config import DATABASE_URL, PROJECT_ROOT

# ---------------------------------------------------------------------------
# Backend selection: PostgreSQL (default) → DuckDB (fallback)
# ---------------------------------------------------------------------------
DEMO_MODE = os.getenv("DEMO_MODE", "").lower() in ("1", "true", "yes")
_DEMO_DIR = PROJECT_ROOT / "data" / "demo"

_backend = None        # "pg" or "duckdb"
_pg_engine = None
_duck_conn = None


def _try_pg():
    """Attempt to connect to PostgreSQL. Returns True on success."""
    global _pg_engine, engine
    try:
        from sqlalchemy import create_engine, text
        _pg_engine = create_engine(DATABASE_URL, echo=False)
        with _pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine = _pg_engine          # expose for ETL imports
        return True
    except Exception:
        _pg_engine = None
        return False


def _init_duckdb():
    """Create an in-memory DuckDB and load demo CSVs as tables."""
    global _duck_conn
    import duckdb

    _duck_conn = duckdb.connect()
    for csv_file in sorted(_DEMO_DIR.glob("*.csv")):
        table = csv_file.stem
        _duck_conn.execute(
            f"CREATE TABLE {table} AS SELECT * FROM read_csv_auto('{csv_file}')"
        )


def _ensure_backend():
    """Initialise the database backend once."""
    global _backend
    if _backend is not None:
        return

    if DEMO_MODE or not _try_pg():
        _init_duckdb()
        _backend = "duckdb"
    else:
        _backend = "pg"


def _convert_params(sql: str, params: dict | None):
    """Convert SQLAlchemy-style :param placeholders to DuckDB $param."""
    if not params:
        return sql, params
    # Replace :name with $name but NOT ::type_cast
    sql = re.sub(r"(?<!:):(\w+)", r"$\1", sql)
    return sql, params


# ---------------------------------------------------------------------------
# Public API — used by all analytics modules
# ---------------------------------------------------------------------------

# Lazy engine reference; set after backend init. ETL modules import this
# directly, but they only run locally where PostgreSQL is available.
engine = None


def _get_engine():
    """Return the SQLAlchemy engine on demand."""
    _ensure_backend()
    return _pg_engine


def run_query(sql: str, params: dict | None = None) -> pd.DataFrame:
    """Execute a SQL query and return a DataFrame."""
    _ensure_backend()
    if _backend == "duckdb":
        sql, params = _convert_params(sql, params)
        if params:
            return _duck_conn.execute(sql, params).df()
        return _duck_conn.execute(sql).df()

    from sqlalchemy import text
    with _pg_engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


def run_sql_file(filepath: str, params: dict | None = None) -> pd.DataFrame:
    """Read a .sql file and execute it, returning a DataFrame."""
    with open(filepath) as f:
        sql = f.read()
    return run_query(sql, params)


def execute(sql: str, params: dict | None = None):
    """Execute a SQL statement (INSERT, CREATE, etc.) without returning rows."""
    _ensure_backend()
    if _backend == "duckdb":
        return  # no-op in demo mode (read-only)
    from sqlalchemy import text
    with _pg_engine.begin() as conn:
        conn.execute(text(sql), params or {})


def date_clause(
    start: datetime.date | None,
    end: datetime.date | None,
    column: str = "e.start_date",
    prefix: str = "AND",
) -> tuple[str, dict]:
    """
    Build a SQL date-range clause and params dict.
    Returns ("AND col >= :start AND col <= :end", {start: ..., end: ...})
    or ("", {}) if no filter.
    """
    if start is None and end is None:
        return "", {}
    parts, params = [], {}
    if start is not None:
        parts.append(f"{prefix} {column} >= :_ds")
        params["_ds"] = str(start)
    if end is not None:
        kw = "AND" if parts else prefix
        parts.append(f"{kw} {column} <= :_de")
        params["_de"] = str(end) + " 23:59:59"
    return " ".join(parts), params
