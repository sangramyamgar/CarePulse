"""
Utilization Trends — Service-line volume, cost, and LOS analysis.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import plotly.express as px
from src.analysis.utilization import (
    get_monthly_volume,
    get_volume_by_class,
    get_los_by_class,
    get_cost_by_month,
    get_top_conditions,
)


st.set_page_config(page_title="Utilization Trends", page_icon="📈", layout="wide")
st.title("📈 Utilization Trends")
st.markdown("How are our services being used? Volume, cost, and length of stay over time.")
st.markdown("---")

# ---- Filters ----
monthly = get_monthly_volume()
if not monthly.empty:
    encounter_types = sorted(monthly["encounter_class"].unique())
    selected_types = st.multiselect(
        "Filter by encounter type",
        encounter_types,
        default=encounter_types,
    )
    filtered = monthly[monthly["encounter_class"].isin(selected_types)]

    # ---- Monthly Volume ----
    st.subheader("Monthly Encounter Volume")
    fig_vol = px.line(
        filtered.groupby("month")["encounter_count"].sum().reset_index(),
        x="month", y="encounter_count",
        title="Total Encounters Per Month",
        labels={"month": "Month", "encounter_count": "Encounters"},
        markers=True,
    )
    fig_vol.update_traces(line_color="#1976D2")
    st.plotly_chart(fig_vol, use_container_width=True)

    # Stacked area by type
    fig_stack = px.area(
        filtered, x="month", y="encounter_count", color="encounter_class",
        title="Volume by Service Line",
        labels={"month": "Month", "encounter_count": "Encounters", "encounter_class": "Type"},
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    st.plotly_chart(fig_stack, use_container_width=True)

st.markdown("---")

# ---- Cost Trends ----
st.subheader("Cost Trends")

left, right = st.columns(2)

cost = get_cost_by_month()
if not cost.empty:
    with left:
        fig_total_cost = px.bar(
            cost, x="month", y="total_cost",
            title="Monthly Total Cost",
            labels={"month": "Month", "total_cost": "Total Cost ($)"},
            color_discrete_sequence=["#FF7043"],
        )
        st.plotly_chart(fig_total_cost, use_container_width=True)

    with right:
        fig_avg_cost = px.line(
            cost, x="month", y="avg_cost",
            title="Average Cost per Encounter",
            labels={"month": "Month", "avg_cost": "Avg Cost ($)"},
            markers=True,
        )
        fig_avg_cost.update_traces(line_color="#26A69A")
        st.plotly_chart(fig_avg_cost, use_container_width=True)

    st.caption(
        "**So what?** Rising total cost with flat average cost means volume is growing. "
        "Rising average cost means per-patient intensity is increasing — investigate case mix."
    )

st.markdown("---")

# ---- Length of Stay ----
st.subheader("Length of Stay by Service Line")

los = get_los_by_class()
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

    st.caption(
        "**So what?** A large gap between mean and median LOS indicates outliers — "
        "a few very long stays pulling the average up. Investigate those cases "
        "for potential care coordination issues."
    )

# ---- Volume by Class ----
st.subheader("Encounter Mix")

by_class = get_volume_by_class()
if not by_class.empty:
    fig_mix = px.bar(
        by_class, x="encounter_class", y="encounter_count",
        text="encounter_count",
        title="Total Encounters by Type",
        labels={"encounter_class": "Type", "encounter_count": "Count"},
        color="encounter_class",
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    fig_mix.update_traces(textposition="outside")
    fig_mix.update_layout(showlegend=False)
    st.plotly_chart(fig_mix, use_container_width=True)
