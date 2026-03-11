"""
Cohort Explorer — Patient demographics and condition burden analysis.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import plotly.express as px
from src.analysis.cohorts import (
    get_patient_demographics,
    get_age_distribution,
    get_chronic_burden,
    get_multi_condition_patients,
    get_encounter_by_age_group,
)
from src.analysis.utilization import get_top_conditions


st.set_page_config(page_title="Cohort Explorer", page_icon="👥", layout="wide")
st.title("👥 Cohort Explorer")
st.markdown("Understand your patient population: who they are, what conditions they carry, and how they use services.")
st.markdown("---")

# ---- Age Distribution ----
left, right = st.columns(2)

with left:
    st.subheader("Patient Age Distribution")
    age_dist = get_age_distribution()
    if not age_dist.empty:
        fig_age = px.bar(
            age_dist,
            x="age_group",
            y="patient_count",
            title="Active Patients by Age Group",
            labels={"age_group": "Age Group", "patient_count": "Patients"},
            color_discrete_sequence=["#1976D2"],
        )
        st.plotly_chart(fig_age, use_container_width=True)

with right:
    st.subheader("Gender & Race Breakdown")
    demo = get_patient_demographics()
    if not demo.empty:
        fig_demo = px.sunburst(
            demo,
            path=["gender", "race"],
            values="patient_count",
            title="Patient Demographics",
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        st.plotly_chart(fig_demo, use_container_width=True)

st.markdown("---")

# ---- Chronic Condition Burden ----
st.subheader("Chronic Condition Burden")

left2, right2 = st.columns(2)

with left2:
    burden = get_chronic_burden()
    if not burden.empty:
        fig_burden = px.bar(
            burden,
            x="chronic_count",
            y="patient_count",
            title="Patients by Number of Chronic Conditions",
            labels={"chronic_count": "# Chronic Conditions", "patient_count": "Patients"},
            color_discrete_sequence=["#FF7043"],
        )
        st.plotly_chart(fig_burden, use_container_width=True)

    st.caption(
        "**So what?** Patients with 3+ chronic conditions drive disproportionate "
        "utilization and cost. These are prime candidates for care management programs."
    )

with right2:
    st.subheader("Top 10 Conditions")
    top_cond = get_top_conditions(10)
    if not top_cond.empty:
        fig_cond = px.bar(
            top_cond,
            y="condition",
            x="frequency",
            orientation="h",
            title="Most Frequent Conditions",
            labels={"condition": "", "frequency": "Occurrences"},
            color_discrete_sequence=["#26A69A"],
        )
        fig_cond.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_cond, use_container_width=True)

st.markdown("---")

# ---- Encounters by Age Group ----
st.subheader("Encounter Mix by Age Group")

enc_age = get_encounter_by_age_group()
if not enc_age.empty:
    fig_enc_age = px.bar(
        enc_age,
        x="age_group",
        y="encounter_count",
        color="encounter_class",
        title="How Different Age Groups Use Services",
        labels={"age_group": "Age Group", "encounter_count": "Encounters", "encounter_class": "Type"},
        barmode="stack",
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    st.plotly_chart(fig_enc_age, use_container_width=True)

    st.caption(
        "**So what?** If older age groups show high emergency usage relative to outpatient, "
        "it may signal inadequate primary care access or chronic disease management gaps."
    )

# ---- Multi-Condition Patients ----
st.subheader("High-Burden Patients (3+ Chronic Conditions)")

min_cond = st.slider("Minimum chronic conditions", 2, 10, 3)
multi = get_multi_condition_patients(min_cond)
if not multi.empty:
    st.dataframe(
        multi[["patient_id", "age", "gender", "chronic_count", "conditions_list"]].head(20),
        use_container_width=True,
    )
    st.caption(f"Showing top 20 patients with ≥{min_cond} chronic conditions.")
else:
    st.info("No patients found with that threshold.")
