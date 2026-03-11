"""
Executive Overview — KPI dashboard for hospital leadership.

Shows headline metrics, monthly trends, and high-level breakdowns.
"""

import sys
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.analysis.readmissions import get_overall_readmission_rate, get_readmission_trend
from src.analysis.utilization import (
    get_headline_metrics,
    get_monthly_volume,
    get_volume_by_class,
    get_payer_mix,
)


st.set_page_config(page_title="Executive Overview", page_icon="📊", layout="wide")
st.title("📊 Executive Overview")
st.markdown("High-level performance metrics for hospital leadership.")
st.markdown("---")

# ---- KPI Cards ----
metrics = get_headline_metrics()
readmit = get_overall_readmission_rate()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Encounters", f"{int(metrics['total_encounters']):,}")
col2.metric("Total Patients", f"{int(metrics['total_patients']):,}")
col3.metric("Avg Length of Stay", f"{metrics['avg_los_days']} days")
col4.metric("30-Day Readmit Rate", f"{readmit['readmission_rate']}%")
col5.metric("Avg Encounter Cost", f"${metrics['avg_cost']:,.0f}")

st.markdown("---")

# ---- Monthly Trend ----
st.subheader("Monthly Encounter Volume")

monthly = get_monthly_volume()
if not monthly.empty:
    fig_monthly = px.bar(
        monthly,
        x="month",
        y="encounter_count",
        color="encounter_class",
        title="Encounter Volume by Month and Type",
        labels={"month": "Month", "encounter_count": "Encounters", "encounter_class": "Type"},
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    fig_monthly.update_layout(xaxis_tickangle=-45, bargap=0.2)
    st.plotly_chart(fig_monthly, use_container_width=True)

    st.caption(
        "**So what?** Look for seasonal spikes (e.g., winter respiratory season) "
        "and whether inpatient volume is growing faster than outpatient — "
        "that could signal capacity pressure."
    )

# ---- Two-column charts ----
left, right = st.columns(2)

with left:
    st.subheader("Encounters by Type")
    by_class = get_volume_by_class()
    if not by_class.empty:
        fig_class = px.pie(
            by_class,
            values="encounter_count",
            names="encounter_class",
            title="Service Line Mix",
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        st.plotly_chart(fig_class, use_container_width=True)

with right:
    st.subheader("Payer Mix")
    payer = get_payer_mix()
    if not payer.empty:
        fig_payer = px.bar(
            payer,
            x="payer",
            y="encounter_count",
            text="pct",
            title="Encounters by Payer",
            labels={"payer": "Payer", "encounter_count": "Encounters"},
            color_discrete_sequence=["#2196F3"],
        )
        fig_payer.update_traces(texttemplate="%{text}%", textposition="outside")
        st.plotly_chart(fig_payer, use_container_width=True)

# ---- Readmission Trend ----
st.subheader("30-Day Readmission Rate Trend")

trend = get_readmission_trend()
if not trend.empty:
    fig_trend = px.line(
        trend,
        x="month",
        y="readmission_rate",
        title="Monthly 30-Day Readmission Rate (%)",
        labels={"month": "Month", "readmission_rate": "Readmission Rate (%)"},
        markers=True,
    )
    fig_trend.update_traces(line_color="#E53935")
    fig_trend.update_layout(yaxis_range=[0, max(trend["readmission_rate"].max() * 1.3, 10)])
    st.plotly_chart(fig_trend, use_container_width=True)

    st.caption(
        "**So what?** A rising readmission rate may indicate gaps in discharge planning, "
        "follow-up care, or patient education. National benchmarks are typically 15-20% "
        "for all-cause 30-day readmission."
    )
