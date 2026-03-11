"""
Data Quality Monitor — Track completeness, validity, and integrity of the data.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.data_quality.checks import (
    get_table_row_counts,
    get_column_completeness,
    get_encounter_date_range,
    get_duplicate_check,
    get_orphan_records,
    get_data_quality_score,
)


st.set_page_config(page_title="Data Quality", page_icon="🔍", layout="wide")
st.title("🔍 Data Quality Monitor")
st.markdown("Trust your data before trusting your dashboards.")
st.markdown("---")

# ---- Overall Score ----
score = get_data_quality_score()

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": "Overall Data Quality Score"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#1976D2"},
            "steps": [
                {"range": [0, 60], "color": "#FFCDD2"},
                {"range": [60, 80], "color": "#FFF9C4"},
                {"range": [80, 100], "color": "#C8E6C9"},
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 90,
            },
        },
    ))
    fig_gauge.update_layout(height=300)
    st.plotly_chart(fig_gauge, use_container_width=True)

st.markdown("""
The score is an average of:
- **Completeness** — % of non-null values across key columns
- **Uniqueness** — % of tables with zero duplicate PKs
- **Referential Integrity** — % of FK checks with zero orphans
""")

st.markdown("---")

# ---- Table Row Counts ----
st.subheader("Table Row Counts")

row_counts = get_table_row_counts()
if not row_counts.empty:
    fig_rows = px.bar(
        row_counts, x="table_name", y="row_count",
        text="row_count",
        title="Rows per Table",
        labels={"table_name": "Table", "row_count": "Rows"},
        color_discrete_sequence=["#1976D2"],
    )
    fig_rows.update_traces(textposition="outside")
    st.plotly_chart(fig_rows, use_container_width=True)

# ---- Date Range ----
st.subheader("Data Freshness")
date_range = get_encounter_date_range()
col1, col2, col3 = st.columns(3)
col1.metric("Earliest Encounter", str(date_range["earliest"]))
col2.metric("Latest Encounter", str(date_range["latest"]))
col3.metric("Months Covered", str(int(date_range["months_covered"])))

st.markdown("---")

# ---- Column Completeness ----
st.subheader("Column Completeness")

completeness = get_column_completeness()
if not completeness.empty:
    # Color-code: green if < 1% null, yellow if 1-5%, red if > 5%
    def color_null(val):
        if val == 0:
            return "background-color: #C8E6C9"
        elif val < 5:
            return "background-color: #FFF9C4"
        else:
            return "background-color: #FFCDD2"

    styled = completeness.style.map(color_null, subset=["null_pct"])
    st.dataframe(
        styled.rename(columns={
            "table_name": "Table",
            "column_name": "Column",
            "total_rows": "Total Rows",
            "null_count": "Null Count",
            "null_pct": "Null %",
        }),
        use_container_width=True,
    )

st.markdown("---")

# ---- Duplicate Check ----
left, right = st.columns(2)

with left:
    st.subheader("Duplicate Check")
    dupes = get_duplicate_check()
    if not dupes.empty:
        st.dataframe(
            dupes.rename(columns={
                "table_name": "Table",
                "total_rows": "Total Rows",
                "distinct_keys": "Distinct PKs",
                "duplicate_count": "Duplicates",
            }),
            use_container_width=True,
        )

with right:
    st.subheader("Referential Integrity")
    orphans = get_orphan_records()
    if not orphans.empty:
        st.dataframe(
            orphans.rename(columns={
                "check_name": "Check",
                "orphan_count": "Orphan Records",
            }),
            use_container_width=True,
        )

st.markdown("---")
st.caption(
    "**Why data quality matters:** Every metric on the other dashboard pages is only as "
    "reliable as the underlying data. In production, these checks would run automatically "
    "after each data load."
)
