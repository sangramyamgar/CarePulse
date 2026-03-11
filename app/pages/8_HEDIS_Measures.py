"""
HEDIS Quality Measures — NCQA-aligned measure reporting.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from app.theme import page_header, insight, section, metric_row, COLORS, PALETTE_SEQ, empty_state

from src.analysis.hedis import (
    get_acr_summary,
    get_acr_trend,
    get_acr_by_payer,
    get_fuh_summary,
    get_fuh_by_payer,
)

st.set_page_config(page_title="HEDIS Measures", page_icon="📋", layout="wide")
page_header(
    "HEDIS Quality Measures",
    "NCQA-aligned performance measures adapted for synthetic data",
    icon="📋",
)

# ── ACR — All-Cause Readmissions ──────────────────────────────────────────
section("ACR — All-Cause Readmissions (Ages 18–64)")

acr = get_acr_summary()
denom = int(acr.get("denominator", 0))
numer = int(acr.get("numerator", 0))
rate = float(acr.get("acr_rate_pct", 0))

metric_row([
    {"label": "Eligible Discharges", "value": f"{denom:,}"},
    {"label": "30-Day Readmissions", "value": f"{numer:,}"},
    {"label": "ACR Rate", "value": f"{rate}%"},
])

insight(
    "NCQA's Plan All-Cause Readmissions (PCR) measure targets adults 18–64. "
    "Lower is better — the national average hovers around 10%. "
    "Rates above 12% flag opportunities for transitional care interventions."
)

# Quarterly trend
acr_trend = get_acr_trend()
if not acr_trend.empty:
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=acr_trend["quarter"],
        y=acr_trend["acr_rate_pct"],
        mode="lines+markers",
        line=dict(color=COLORS["primary"], width=2.5),
        marker=dict(size=7),
        fill="tozeroy",
        fillcolor="rgba(0,87,184,0.06)",
        name="ACR Rate",
    ))
    fig_trend.add_hline(
        y=10, line_dash="dash", line_color=COLORS["text_muted"],
        annotation_text="National Avg ~10%",
        annotation_font_color=COLORS["text_muted"],
    )
    fig_trend.update_layout(
        yaxis_title="ACR Rate (%)",
        xaxis_title="Quarter",
        height=360,
    )
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    empty_state("No ACR trend data available.")

# By payer
acr_payer = get_acr_by_payer()
if not acr_payer.empty:
    st.markdown("**ACR Rate by Payer**")
    fig_payer = px.bar(
        acr_payer, x="payer", y="acr_rate_pct", text="acr_rate_pct",
        color_discrete_sequence=[COLORS["primary"]],
        labels={"payer": "", "acr_rate_pct": "ACR Rate (%)"},
    )
    fig_payer.update_traces(texttemplate="%{text}%", textposition="outside")
    fig_payer.update_layout(showlegend=False, height=340)
    st.plotly_chart(fig_payer, use_container_width=True)

st.markdown("---")

# ── FUH — Follow-Up After Hospitalization for Mental Illness ──────────────
section("FUH — Follow-Up After MH Hospitalization")

fuh = get_fuh_summary()
fuh_denom = int(fuh.get("denominator", 0))

if fuh_denom > 0:
    metric_row([
        {"label": "MH Discharges", "value": f"{fuh_denom:,}"},
        {"label": "FUH-7 Rate (7-day)", "value": f"{fuh.get('fuh_7d_rate_pct', 0)}%"},
        {"label": "FUH-30 Rate (30-day)", "value": f"{fuh.get('fuh_30d_rate_pct', 0)}%"},
    ])

    insight(
        "FUH tracks timely outpatient follow-up after a mental health hospitalization. "
        "NCQA targets: FUH-7 ≥ 40%, FUH-30 ≥ 60%. Low rates indicate gaps in behavioral health "
        "care coordination."
    )

    # Comparison bar: 7-day vs 30-day
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(
        x=["FUH-7 (7 day)", "FUH-30 (30 day)"],
        y=[float(fuh.get("fuh_7d_rate_pct", 0)), float(fuh.get("fuh_30d_rate_pct", 0))],
        marker_color=[COLORS["primary"], COLORS["secondary"]],
        text=[f"{fuh.get('fuh_7d_rate_pct', 0)}%", f"{fuh.get('fuh_30d_rate_pct', 0)}%"],
        textposition="outside",
    ))
    fig_comp.update_layout(
        yaxis_title="Follow-Up Rate (%)",
        height=320, showlegend=False,
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    # By payer
    fuh_payer = get_fuh_by_payer()
    if not fuh_payer.empty:
        st.markdown("**FUH Rates by Payer**")
        fig_fuh_p = go.Figure()
        fig_fuh_p.add_trace(go.Bar(
            name="FUH-7", x=fuh_payer["payer"], y=fuh_payer["fuh_7d_rate_pct"],
            marker_color=COLORS["primary_light"],
            text=fuh_payer["fuh_7d_rate_pct"].apply(lambda v: f"{v}%"),
            textposition="outside",
        ))
        fig_fuh_p.add_trace(go.Bar(
            name="FUH-30", x=fuh_payer["payer"], y=fuh_payer["fuh_30d_rate_pct"],
            marker_color=COLORS["secondary"],
            text=fuh_payer["fuh_30d_rate_pct"].apply(lambda v: f"{v}%"),
            textposition="outside",
        ))
        fig_fuh_p.update_layout(
            barmode="group", yaxis_title="Rate (%)", height=360,
        )
        st.plotly_chart(fig_fuh_p, use_container_width=True)
else:
    empty_state(
        "No mental-health-related inpatient encounters found in the data. "
        "FUH requires conditions like depression, anxiety, bipolar disorder, or schizophrenia."
    )

# ── Measure Definitions Reference ─────────────────────────────────────────
st.markdown("---")
section("Measure Definitions Reference")

with st.expander("ACR — Plan All-Cause Readmissions (NCQA PCR)", expanded=False):
    st.markdown("""
| Attribute | Detail |
|-----------|--------|
| **Denominator** | Acute inpatient discharges, ages 18–64 |
| **Numerator** | Unplanned readmission within 30 days |
| **Exclusions** | Deaths during index stay, planned readmissions |
| **Direction** | Lower is better |
| **Benchmark** | National ~10% |
| **Source** | NCQA HEDIS MY 2024 |
""")

with st.expander("FUH — Follow-Up After Hospitalization for Mental Illness", expanded=False):
    st.markdown("""
| Attribute | Detail |
|-----------|--------|
| **Denominator** | Inpatient discharges with principal MH diagnosis |
| **Numerator (7d)** | Outpatient MH visit within 7 days of discharge |
| **Numerator (30d)** | Outpatient MH visit within 30 days of discharge |
| **Direction** | Higher is better |
| **Benchmark** | FUH-7 ≥ 40%, FUH-30 ≥ 60% |
| **Source** | NCQA HEDIS MY 2024 |
""")
