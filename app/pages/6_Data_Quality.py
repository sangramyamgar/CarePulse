"""
Data Quality Monitor — Track completeness, validity, and integrity of the data.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from app.theme import page_header, insight, section, metric_row, COLORS
from src.data_quality.checks import (
    get_table_row_counts,
    get_column_completeness,
    get_encounter_date_range,
    get_duplicate_check,
    get_orphan_records,
    get_data_quality_score,
)

st.set_page_config(page_title="Data Quality", page_icon="🔍", layout="wide")
page_header("Data Quality Monitor", "Trust your data before trusting your dashboards.", icon="🔍")

# ---- Overall Score ----
score = get_data_quality_score()

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": "Overall Data Quality Score", "font": {"size": 16, "color": COLORS["text"]}},
        number={"font": {"size": 48, "color": COLORS["primary"]}, "suffix": "%"},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": COLORS["border"]},
            "bar": {"color": COLORS["primary"], "thickness": 0.3},
            "bgcolor": "#F8FAFC",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 60], "color": "#FEE2E2"},
                {"range": [60, 80], "color": "#FEF9C3"},
                {"range": [80, 100], "color": "#DCFCE7"},
            ],
            "threshold": {
                "line": {"color": COLORS["danger"], "width": 3},
                "thickness": 0.75,
                "value": 90,
            },
        },
    ))
    fig_gauge.update_layout(height=280, margin=dict(t=40, b=0))
    st.plotly_chart(fig_gauge, use_container_width=True)

st.markdown("""
<div style="text-align:center; color:#64748B; font-size:0.88rem; margin-bottom:1.5rem;">
    Composite of <strong>Completeness</strong> (non-null %), <strong>Uniqueness</strong> (zero duplicates), and <strong>Referential Integrity</strong> (zero orphans).
</div>
""", unsafe_allow_html=True)

# ---- Table Row Counts ----
section("Table Row Counts")

row_counts = get_table_row_counts()
if not row_counts.empty:
    fig_rows = px.bar(
        row_counts, x="table_name", y="row_count", text="row_count",
        labels={"table_name": "", "row_count": "Rows"},
        color_discrete_sequence=[COLORS["primary"]],
    )
    fig_rows.update_traces(textposition="outside")
    fig_rows.update_layout(showlegend=False)
    st.plotly_chart(fig_rows, use_container_width=True)

# ---- Date Range ----
section("Data Freshness")
date_range = get_encounter_date_range()
metric_row([
    {"label": "Earliest Encounter", "value": str(date_range["earliest"])},
    {"label": "Latest Encounter", "value": str(date_range["latest"])},
    {"label": "Months Covered", "value": str(int(date_range["months_covered"]))},
])

# ---- Column Completeness ----
section("Column Completeness")

completeness = get_column_completeness()
if not completeness.empty:
    def color_null(val):
        if val == 0:
            return "background-color: #DCFCE7"
        elif val < 5:
            return "background-color: #FEF9C3"
        else:
            return "background-color: #FEE2E2"

    styled = completeness.style.map(color_null, subset=["null_pct"])
    st.dataframe(styled, use_container_width=True)
    st.download_button("⬇ Export CSV", completeness.to_csv(index=False), "column_completeness.csv", "text/csv")

# ---- Duplicate + Orphan checks ----
left, right = st.columns(2)

with left:
    section("Duplicate Check")
    dupes = get_duplicate_check()
    if not dupes.empty:
        st.dataframe(
            dupes.rename(columns={
                "table_name": "Table", "total_rows": "Total Rows",
                "distinct_keys": "Distinct PKs", "duplicate_count": "Duplicates",
            }),
            use_container_width=True,
        )

with right:
    section("Referential Integrity")
    orphans = get_orphan_records()
    if not orphans.empty:
        st.dataframe(
            orphans.rename(columns={
                "check_name": "Check", "orphan_count": "Orphan Records",
            }),
            use_container_width=True,
        )

insight(
    "Every metric on the other dashboard pages is only as reliable as the underlying data. "
    "In production, these checks would run automatically after each data load."
)
