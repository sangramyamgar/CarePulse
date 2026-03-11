"""
Facility / Provider Drilldown — Compare performance across sites and providers.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import plotly.express as px
from src.analysis.facilities import (
    get_facility_comparison,
    get_facility_monthly_volume,
    get_provider_summary,
    get_facility_readmission_comparison,
)


st.set_page_config(page_title="Facility Drilldown", page_icon="🏢", layout="wide")
st.title("🏢 Facility / Provider Drilldown")
st.markdown("Compare facilities on key performance metrics and drill into provider-level data.")
st.markdown("---")

# ---- Facility Comparison Table ----
st.subheader("Facility Comparison")

comp = get_facility_comparison()
if not comp.empty:
    st.dataframe(
        comp.rename(columns={
            "facility_name": "Facility",
            "city": "City",
            "total_encounters": "Encounters",
            "unique_patients": "Patients",
            "avg_encounter_cost": "Avg Cost ($)",
            "avg_los_days": "Avg LOS (days)",
            "readmit_rate_pct": "Readmit Rate (%)",
        }),
        use_container_width=True,
    )

    st.caption(
        "**So what?** Facilities with both high readmission rates and high ALOS "
        "may have systemic discharge planning issues. Low-volume, high-cost facilities "
        "may need case-mix optimization."
    )

st.markdown("---")

# ---- Readmission Rate Comparison ----
st.subheader("Readmission Rate by Facility")

readmit_comp = get_facility_readmission_comparison()
if not readmit_comp.empty:
    fig_readmit = px.bar(
        readmit_comp, x="facility_name", y="readmission_rate",
        text="readmission_rate",
        title="30-Day Readmission Rate by Facility",
        labels={"facility_name": "Facility", "readmission_rate": "Rate (%)"},
        color="readmission_rate",
        color_continuous_scale="RdYlGn_r",  # Red = bad, Green = good
    )
    fig_readmit.update_traces(texttemplate="%{text}%", textposition="outside")
    st.plotly_chart(fig_readmit, use_container_width=True)

st.markdown("---")

# ---- Facility Monthly Trend ----
st.subheader("Facility Volume Over Time")

if not comp.empty:
    facility_names = comp["facility_name"].tolist()
    selected_facility = st.selectbox("Select a facility", facility_names)

    facility_monthly = get_facility_monthly_volume(selected_facility)
    if not facility_monthly.empty:
        fig_monthly = px.bar(
            facility_monthly,
            x="month", y="encounter_count", color="encounter_class",
            title=f"{selected_facility} — Monthly Volume",
            labels={"month": "Month", "encounter_count": "Encounters", "encounter_class": "Type"},
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        st.plotly_chart(fig_monthly, use_container_width=True)

st.markdown("---")

# ---- Provider Summary ----
st.subheader("Provider Summary")

providers = get_provider_summary()
if not providers.empty:
    # Filter by facility
    if not comp.empty:
        fac_filter = st.selectbox("Filter by facility", ["All"] + facility_names, key="prov_fac")
        if fac_filter != "All":
            providers = providers[providers["facility_name"] == fac_filter]

    st.dataframe(
        providers.rename(columns={
            "provider_name": "Provider",
            "specialty": "Specialty",
            "facility_name": "Facility",
            "encounter_count": "Encounters",
            "unique_patients": "Patients",
            "avg_cost": "Avg Cost ($)",
        }).head(30),
        use_container_width=True,
    )

    st.caption("Showing top 30 providers by encounter volume.")
