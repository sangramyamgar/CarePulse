"""
Readmission & Revisit Analysis — Deep-dive into 30-day readmission patterns.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
from src.analysis.readmissions import (
    get_overall_readmission_rate,
    get_readmission_trend,
    get_readmission_by_age_group,
    get_readmission_by_condition,
    get_readmission_by_payer,
    get_readmission_by_chronic_count,
    get_days_to_readmit_distribution,
)


st.set_page_config(page_title="Readmission Analysis", page_icon="🔄", layout="wide")
st.title("🔄 Readmission & Revisit Analysis")
st.markdown("Which patients come back within 30 days — and why?")
st.markdown("---")

# ---- Headline Metrics ----
overall = get_overall_readmission_rate()
col1, col2, col3 = st.columns(3)
col1.metric("Total Inpatient Discharges", f"{int(overall['total_inpatient']):,}")
col2.metric("30-Day Readmissions", f"{int(overall['readmissions']):,}")
col3.metric("Readmission Rate", f"{overall['readmission_rate']}%")

st.markdown("---")

# ---- Readmission Trend ----
st.subheader("Monthly Readmission Rate Trend")
trend = get_readmission_trend()
if not trend.empty:
    fig = px.area(
        trend, x="month", y="readmission_rate",
        title="30-Day Readmission Rate Over Time",
        labels={"month": "Month", "readmission_rate": "Rate (%)"},
    )
    fig.update_traces(fillcolor="rgba(229, 57, 53, 0.2)", line_color="#E53935")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ---- Days to Readmission Distribution ----
st.subheader("Days to Readmission Distribution")
dist = get_days_to_readmit_distribution()
if not dist.empty:
    fig_dist = px.histogram(
        dist, x="days_to_readmit", nbins=30,
        title="How Soon Do Patients Return?",
        labels={"days_to_readmit": "Days After Discharge"},
        color_discrete_sequence=["#7B1FA2"],
    )
    fig_dist.add_vline(x=30, line_dash="dash", line_color="red",
                       annotation_text="30-day cutoff")
    st.plotly_chart(fig_dist, use_container_width=True)

    st.caption(
        "**So what?** A spike in the first 7 days suggests discharge process issues. "
        "A cluster around day 20-30 may indicate scheduled follow-ups being counted as readmissions."
    )

st.markdown("---")

# ---- Cohort Breakdowns ----
st.subheader("Readmission Rate by Cohort")

tab1, tab2, tab3, tab4 = st.tabs(["By Age Group", "By Condition", "By Payer", "By Chronic Count"])

with tab1:
    by_age = get_readmission_by_age_group()
    if not by_age.empty:
        fig_age = px.bar(
            by_age, x="age_group", y="readmission_rate_pct",
            text="readmission_rate_pct",
            title="Readmission Rate by Age Group",
            labels={"age_group": "Age Group", "readmission_rate_pct": "Rate (%)"},
            color_discrete_sequence=["#1976D2"],
        )
        fig_age.update_traces(texttemplate="%{text}%", textposition="outside")
        st.plotly_chart(fig_age, use_container_width=True)

        st.caption(
            "**So what?** Higher rates in elderly groups (60-74, 75+) are expected but actionable. "
            "Targeted transitional care programs can reduce these rates by 20-30%."
        )

with tab2:
    top_n = st.slider("Top N conditions", 5, 20, 10, key="cond_slider")
    by_cond = get_readmission_by_condition(top_n)
    if not by_cond.empty:
        fig_cond = px.bar(
            by_cond, y="primary_condition", x="readmission_rate",
            orientation="h", text="readmission_rate",
            title=f"Readmission Rate — Top {top_n} Conditions",
            labels={"primary_condition": "", "readmission_rate": "Rate (%)"},
            color_discrete_sequence=["#FF7043"],
        )
        fig_cond.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_cond.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_cond, use_container_width=True)

with tab3:
    by_payer = get_readmission_by_payer()
    if not by_payer.empty:
        fig_payer = px.bar(
            by_payer, x="payer", y="readmission_rate",
            text="readmission_rate",
            title="Readmission Rate by Payer",
            labels={"payer": "Payer", "readmission_rate": "Rate (%)"},
            color_discrete_sequence=["#26A69A"],
        )
        fig_payer.update_traces(texttemplate="%{text}%", textposition="outside")
        st.plotly_chart(fig_payer, use_container_width=True)

        st.caption(
            "**So what?** Medicare typically has the highest readmission rates. "
            "CMS penalizes hospitals with excess readmissions through the HRRP program."
        )

with tab4:
    by_chronic = get_readmission_by_chronic_count()
    if not by_chronic.empty:
        fig_chronic = px.line(
            by_chronic, x="chronic_count", y="readmission_rate",
            markers=True,
            title="Readmission Rate vs. Chronic Condition Count",
            labels={"chronic_count": "# Chronic Conditions", "readmission_rate": "Rate (%)"},
        )
        fig_chronic.update_traces(line_color="#E53935")
        st.plotly_chart(fig_chronic, use_container_width=True)

        st.caption(
            "**So what?** If readmission rate increases linearly with chronic count, "
            "multimorbidity is a key driver. Integrated care models are the recommended intervention."
        )
