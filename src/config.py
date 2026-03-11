"""
Central configuration for CarePulse.
Reads database credentials from .env file and provides constants used across the project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
SQL_DIR = PROJECT_ROOT / "sql"

# ---------------------------------------------------------------------------
# Load environment variables from .env
# ---------------------------------------------------------------------------
load_dotenv(PROJECT_ROOT / ".env")

# ---------------------------------------------------------------------------
# Database settings
# ---------------------------------------------------------------------------
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "carepulse")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

# ---------------------------------------------------------------------------
# Analytics constants
# ---------------------------------------------------------------------------
READMISSION_WINDOW_DAYS = 30

# Age group bins used throughout the project
AGE_BINS = [0, 18, 30, 45, 60, 75, 120]
AGE_LABELS = ["0-17", "18-29", "30-44", "45-59", "60-74", "75+"]

# Encounter classes we treat as "inpatient" for readmission logic
INPATIENT_CLASSES = ["inpatient"]
