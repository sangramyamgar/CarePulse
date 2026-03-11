"""
Global sidebar filters — date range and encounter type.

Every analytics page imports `get_date_filter()` to get the user-selected
date range, which is then passed to query functions.
"""

import streamlit as st
import datetime
from src.data_quality.checks import get_encounter_date_range


def get_date_filter() -> tuple[datetime.date, datetime.date]:
    """
    Render a date-range picker in the sidebar and return (start, end).
    Uses the actual data range as defaults.
    """
    date_range = get_encounter_date_range()
    earliest = date_range["earliest"]
    latest = date_range["latest"]

    # Convert to date objects if they're strings/timestamps
    if not isinstance(earliest, datetime.date):
        earliest = datetime.date.fromisoformat(str(earliest)[:10])
    if not isinstance(latest, datetime.date):
        latest = datetime.date.fromisoformat(str(latest)[:10])

    st.sidebar.markdown("---")
    st.sidebar.markdown("**📅 Date Range**")

    start = st.sidebar.date_input(
        "From", value=earliest, min_value=earliest, max_value=latest, key="global_start",
    )
    end = st.sidebar.date_input(
        "To", value=latest, min_value=earliest, max_value=latest, key="global_end",
    )

    if start > end:
        st.sidebar.error("Start date must be before end date.")
        start, end = earliest, latest

    return start, end
