"""
Executive Overview — KPI dashboard for hospital leadership.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from app.theme import page_header, insight, section, metric_row, COLORS, PALETTE_SEQ
from app.filters import get_date_filter
from src.analysis.readmissions import get_overall_readmission_rate, get_readmission_trend
from src.analysis.utilization import (
    get_headline_metrics,
    get_monthly_volume,
    get_volume_by_class,
    get_payer_mix,
)

st.set_page_config(page_title="Executive Overview", page_icon="📊", layout="wide")
page_header("Executive Overview", "High-level performance metrics for hospital leadership.", icon="📊")

date_start, date_end = get_date_filter()

# ---- KPI Cards ----
metrics = get_headline_metrics(date_start, date_end)
readmit = get_overall_readmission_rate(date_start, date_end)

metric_row([
    {"label": "Total Encounters", "value": f"{int(metrics['total_encounters']):,}"},
    {"label": "Total Patients", "value": f"{int(metrics['total_patients']):,}"},
    {"label": "Avg Length of Stay", "value": f"{metrics['avg_los_days']} days"},
    {"label": "30-Day Readmit Rate", "value": f"{readmit['readmission_rate']}%"},
    {"label": "Avg Encounter Cost", "value": f"${metrics['avg_cost']:,.0f}"},
])

# ---- Monthly Trend ----
section("Monthly Encounter Volume")

monthly = get_monthly_volume(date_start, date_end)
if not monthly.empty:
    fig_monthly = px.bar(
        monthly, x="month", y="encounter_count", color="encounter_class",
        labels={"month": "", "encounter_count": "Encounters", "encounter_class": "Type"},
        color_discrete_sequence=PALETTE_SEQ,
    )
    fig_monthly.update_layout(xaxis_tickangle=-45, bargap=0.2)
    st.plotly_chart(fig_monthly, use_container_width=True)
    st.download_button("⬇ Export CSV", monthly.to_csv(index=False), "monthly_volume.csv", "text/csv")

    insight(
        "Look for seasonal spikes (e.g., winter respiratory season) and whether "
        "inpatient volume is growing faster than outpatient — that could signal capacity pressure."
    )

# ---- Two-column charts ----
left, right = st.columns(2)

with left:
    section("Service Line Mix")
    by_class = get_volume_by_class(date_start, date_end)
    if not by_class.empty:
        fig_class = px.pie(
            by_class, values="encounter_count", names="encounter_class",
            color_discrete_sequence=PALETTE_SEQ,
            hole=0.45,
        )
        fig_class.update_traces(textposition="inside", textinfo="percent+label",
                                textfont_size=12)
        fig_class.update_layout(showlegend=False, margin=dict(t=16, b=16))
        st.plotly_chart(fig_class, use_container_width=True)

with right:
    section("Payer Mix")
    payer = get_payer_mix(date_start, date_end)
    if not payer.empty:
        fig_payer = px.bar(
            payer, x="payer", y="encounter_count", text="pct",
            labels={"payer": "", "encounter_count": "Encounters"},
            color_discrete_sequence=[COLORS["primary"]],
        )
        fig_payer.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_payer.update_layout(showlegend=False)
        st.plotly_chart(fig_payer, use_container_width=True)

# ---- Readmission Trend ----
section("30-Day Readmission Rate Trend")

trend = get_readmission_trend(date_start, date_end)
if not trend.empty:
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=trend["month"], y=trend["readmission_rate"],
        mode="lines+markers",
        line=dict(color=COLORS["danger"], width=2.5),
        marker=dict(size=7, color=COLORS["danger"]),
        fill="tozeroy",
        fillcolor="rgba(239,68,68,0.08)",
        name="Readmit Rate",
    ))
    fig_trend.update_layout(
        yaxis_title="Rate (%)",
        yaxis_range=[0, max(trend["readmission_rate"].max() * 1.3, 10)],
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    st.download_button("⬇ Export CSV", trend.to_csv(index=False), "readmission_trend.csv", "text/csv")

    insight(
        "A rising readmission rate may indicate gaps in discharge planning, "
        "follow-up care, or patient education. National benchmarks are typically 15–20% "
        "for all-cause 30-day readmission."
    )
