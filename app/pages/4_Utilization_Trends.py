"""
Utilization Trends — Service-line volume, cost, and LOS analysis.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from app.theme import page_header, insight, section, COLORS, PALETTE_SEQ
from app.filters import get_date_filter
from src.analysis.utilization import (
    get_monthly_volume,
    get_volume_by_class,
    get_los_by_class,
    get_cost_by_month,
    get_top_conditions,
)

st.set_page_config(page_title="Utilization Trends", page_icon="📈", layout="wide")
page_header("Utilization Trends", "How are our services being used? Volume, cost, and length of stay over time.", icon="📈")

date_start, date_end = get_date_filter()

# ---- Filters ----
monthly = get_monthly_volume(date_start, date_end)
if not monthly.empty:
    encounter_types = sorted(monthly["encounter_class"].unique())
    selected_types = st.multiselect(
        "Filter by encounter type", encounter_types, default=encounter_types,
    )
    filtered = monthly[monthly["encounter_class"].isin(selected_types)]

    # ---- Monthly Volume ----
    section("Monthly Encounter Volume")

    fig_vol = go.Figure()
    agg = filtered.groupby("month")["encounter_count"].sum().reset_index()
    fig_vol.add_trace(go.Scatter(
        x=agg["month"], y=agg["encounter_count"],
        mode="lines+markers",
        line=dict(color=COLORS["primary"], width=2.5),
        marker=dict(size=6),
        name="Total",
    ))
    fig_vol.update_layout(yaxis_title="Encounters")
    st.plotly_chart(fig_vol, use_container_width=True)

    # Stacked area by type
    fig_stack = px.area(
        filtered, x="month", y="encounter_count", color="encounter_class",
        labels={"month": "", "encounter_count": "Encounters", "encounter_class": "Type"},
        color_discrete_sequence=PALETTE_SEQ,
    )
    st.plotly_chart(fig_stack, use_container_width=True)

# ---- Cost Trends ----
section("Cost Trends")

left, right = st.columns(2)
cost = get_cost_by_month(date_start, date_end)
if not cost.empty:
    with left:
        fig_total_cost = px.bar(
            cost, x="month", y="total_cost",
            labels={"month": "", "total_cost": "Total Cost ($)"},
            color_discrete_sequence=[COLORS["accent"]],
        )
        fig_total_cost.update_layout(showlegend=False)
        st.plotly_chart(fig_total_cost, use_container_width=True)

    with right:
        fig_avg_cost = go.Figure()
        fig_avg_cost.add_trace(go.Scatter(
            x=cost["month"], y=cost["avg_cost"],
            mode="lines+markers",
            line=dict(color=COLORS["secondary"], width=2.5),
            marker=dict(size=6),
            name="Avg Cost",
        ))
        fig_avg_cost.update_layout(yaxis_title="Avg Cost ($)")
        st.plotly_chart(fig_avg_cost, use_container_width=True)

    insight(
        "Rising total cost with flat average cost means volume is growing. "
        "Rising average cost means per-patient intensity is increasing — investigate case mix."
    )

# ---- Length of Stay ----
section("Length of Stay by Service Line")

los = get_los_by_class(date_start, date_end)
if not los.empty:
    st.dataframe(
        los.rename(columns={
            "encounter_class": "Type",
            "encounters": "Encounters",
            "avg_los": "Avg LOS (days)",
            "median_los": "Median LOS (days)",
        }),
        use_container_width=True,
    )
    st.download_button("⬇ Export CSV", los.to_csv(index=False), "los_by_class.csv", "text/csv")

    insight(
        "A large gap between mean and median LOS indicates outliers — "
        "a few very long stays pulling the average up. Investigate for care coordination issues."
    )

# ---- Volume by Class ----
section("Encounter Mix")

by_class = get_volume_by_class(date_start, date_end)
if not by_class.empty:
    fig_mix = px.bar(
        by_class, x="encounter_class", y="encounter_count", text="encounter_count",
        labels={"encounter_class": "", "encounter_count": "Count"},
        color="encounter_class",
        color_discrete_sequence=PALETTE_SEQ,
    )
    fig_mix.update_traces(textposition="outside")
    fig_mix.update_layout(showlegend=False)
    st.plotly_chart(fig_mix, use_container_width=True)
