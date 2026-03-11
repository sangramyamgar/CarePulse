"""
Readmission & Revisit Analysis — Deep-dive into 30-day readmission patterns.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from app.theme import page_header, insight, section, metric_row, COLORS, PALETTE_SEQ
from app.filters import get_date_filter
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
page_header("Readmission & Revisit Analysis", "Which patients come back within 30 days — and why?", icon="🔄")

date_start, date_end = get_date_filter()

# ---- Headline Metrics ----
overall = get_overall_readmission_rate(date_start, date_end)
metric_row([
    {"label": "Total Inpatient Discharges", "value": f"{int(overall['total_inpatient']):,}"},
    {"label": "30-Day Readmissions", "value": f"{int(overall['readmissions']):,}"},
    {"label": "Readmission Rate", "value": f"{overall['readmission_rate']}%"},
])

# ---- Readmission Trend ----
section("Monthly Readmission Rate Trend")
trend = get_readmission_trend(date_start, date_end)
if not trend.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=trend["month"], y=trend["readmission_rate"],
        mode="lines+markers",
        line=dict(color=COLORS["danger"], width=2.5),
        marker=dict(size=7),
        fill="tozeroy",
        fillcolor="rgba(239,68,68,0.08)",
        name="Readmit Rate",
    ))
    fig.update_layout(yaxis_title="Rate (%)")
    st.plotly_chart(fig, use_container_width=True)

# ---- Days to Readmission Distribution ----
section("Days to Readmission Distribution")
dist = get_days_to_readmit_distribution()
if not dist.empty:
    fig_dist = px.histogram(
        dist, x="days_to_readmit", nbins=30,
        labels={"days_to_readmit": "Days After Discharge"},
        color_discrete_sequence=[COLORS["primary"]],
    )
    fig_dist.add_vline(x=30, line_dash="dash", line_color=COLORS["danger"],
                       annotation_text="30-day cutoff",
                       annotation_font_color=COLORS["danger"])
    st.plotly_chart(fig_dist, use_container_width=True)
    st.download_button("⬇ Export CSV", dist.to_csv(index=False), "readmit_distribution.csv", "text/csv")

    insight(
        "A spike in the first 7 days suggests discharge process issues. "
        "A cluster around day 20–30 may indicate scheduled follow-ups being counted as readmissions."
    )

# ---- Cohort Breakdowns ----
section("Readmission Rate by Cohort")

tab1, tab2, tab3, tab4 = st.tabs(["By Age Group", "By Condition", "By Payer", "By Chronic Count"])

with tab1:
    by_age = get_readmission_by_age_group()
    if not by_age.empty:
        fig_age = px.bar(
            by_age, x="age_group", y="readmission_rate_pct", text="readmission_rate_pct",
            labels={"age_group": "", "readmission_rate_pct": "Rate (%)"},
            color_discrete_sequence=[COLORS["primary"]],
        )
        fig_age.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_age.update_layout(showlegend=False)
        st.plotly_chart(fig_age, use_container_width=True)
        st.download_button("⬇ Export CSV", by_age.to_csv(index=False), "readmit_by_age.csv", "text/csv")

        insight(
            "Higher rates in elderly groups (60–74, 75+) are expected but actionable. "
            "Targeted transitional care programs can reduce these rates by 20–30%."
        )

with tab2:
    top_n = st.slider("Top N conditions", 5, 20, 10, key="cond_slider")
    by_cond = get_readmission_by_condition(top_n)
    if not by_cond.empty:
        fig_cond = px.bar(
            by_cond, y="primary_condition", x="readmission_rate", orientation="h",
            text="readmission_rate",
            labels={"primary_condition": "", "readmission_rate": "Rate (%)"},
            color_discrete_sequence=[COLORS["accent"]],
        )
        fig_cond.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_cond.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)
        st.plotly_chart(fig_cond, use_container_width=True)

with tab3:
    by_payer = get_readmission_by_payer()
    if not by_payer.empty:
        fig_payer = px.bar(
            by_payer, x="payer", y="readmission_rate", text="readmission_rate",
            labels={"payer": "", "readmission_rate": "Rate (%)"},
            color_discrete_sequence=[COLORS["secondary"]],
        )
        fig_payer.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_payer.update_layout(showlegend=False)
        st.plotly_chart(fig_payer, use_container_width=True)

        insight(
            "Medicare typically has the highest readmission rates. "
            "CMS penalizes hospitals with excess readmissions through the HRRP program."
        )

with tab4:
    by_chronic = get_readmission_by_chronic_count()
    if not by_chronic.empty:
        fig_chronic = go.Figure()
        fig_chronic.add_trace(go.Scatter(
            x=by_chronic["chronic_count"], y=by_chronic["readmission_rate"],
            mode="lines+markers",
            line=dict(color=COLORS["danger"], width=2.5),
            marker=dict(size=8),
        ))
        fig_chronic.update_layout(
            xaxis_title="# Chronic Conditions",
            yaxis_title="Readmission Rate (%)",
        )
        st.plotly_chart(fig_chronic, use_container_width=True)

        insight(
            "If readmission rate increases linearly with chronic count, "
            "multimorbidity is a key driver. Integrated care models are the recommended intervention."
        )
