"""
CarePulse — Home Page
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from app.theme import inject_css, COLORS

st.set_page_config(
    page_title="CarePulse Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

# ---- Hero ----
st.markdown(
    f"""
    <div style="
        background: linear-gradient(135deg, {COLORS['primary']} 0%, #003D82 100%);
        border-radius: 16px;
        padding: 48px 40px;
        margin-bottom: 2rem;
        color: white;
    ">
        <h1 style="margin:0; font-size:2.5rem; color:white !important; font-weight:700;">
            🏥 CarePulse
        </h1>
        <p style="margin:8px 0 0; font-size:1.15rem; color:#93C5FD; font-weight:400;">
            Readmission &amp; Utilization Analytics Platform
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <p style="font-size:1.05rem; color:#334155; line-height:1.7; max-width:720px;">
    CarePulse helps hospital leadership understand <strong>patient readmission patterns</strong>,
    <strong>utilization trends</strong>, and <strong>operational performance</strong> across facilities —
    powered by a clean ETL pipeline, HEDIS-aligned measures, and automated data quality monitoring.
    </p>
    """,
    unsafe_allow_html=True,
)

# ---- Navigation cards ----
st.markdown("<h3 style='margin-top:2rem; color:#1E293B;'>Explore the Dashboard</h3>", unsafe_allow_html=True)

cards = [
    ("📊", "Executive Overview", "KPIs, volume trends, payer mix, and readmission rates at a glance."),
    ("👥", "Cohort Explorer", "Patient demographics, age groups, and chronic condition burden."),
    ("🔄", "Readmission Analysis", "Deep-dive into 30-day readmission drivers by cohort."),
    ("📈", "Utilization Trends", "Monthly volume, cost trends, length of stay, and service-line mix."),
    ("🏢", "Facility Drilldown", "Side-by-side facility comparison and provider-level detail."),
    ("🔍", "Data Quality", "Completeness, validity, referential integrity, and overall DQ score."),
    ("🧠", "Model Explainability", "Risk model performance, feature importance, and patient scoring."),
    ("🏛️", "HEDIS Measures", "ACR and FUH measures aligned to NCQA / CMS specifications."),
]

for i in range(0, len(cards), 4):
    cols = st.columns(4)
    for j, col in enumerate(cols):
        idx = i + j
        if idx < len(cards):
            icon, title, desc = cards[idx]
            col.markdown(
                f"""
                <div style="
                    background: #F8FAFC;
                    border: 1px solid #E2E8F0;
                    border-radius: 12px;
                    padding: 20px;
                    height: 160px;
                ">
                    <div style="font-size:1.5rem;">{icon}</div>
                    <p style="font-weight:600; color:#0057B8; margin:8px 0 4px; font-size:0.95rem;">
                        {title}
                    </p>
                    <p style="color:#64748B; font-size:0.82rem; line-height:1.4; margin:0;">
                        {desc}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ---- Key metrics legend ----
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="display:flex; gap:32px; flex-wrap:wrap; margin-bottom:1rem;">
        <div>
            <span style="font-weight:600; color:#0057B8;">30-Day Readmission Rate</span>
            <span style="color:#64748B; font-size:0.85rem;"> — % of inpatient discharges with re-admission within 30 days</span>
        </div>
        <div>
            <span style="font-weight:600; color:#0057B8;">ALOS</span>
            <span style="color:#64748B; font-size:0.85rem;"> — Average Length of Stay (inpatient days)</span>
        </div>
        <div>
            <span style="font-weight:600; color:#0057B8;">HEDIS ACR</span>
            <span style="color:#64748B; font-size:0.85rem;"> — All-Cause Readmission rate per NCQA specification</span>
        </div>
    </div>
    <p style="color:#94A3B8; font-size:0.8rem;">
        Built with synthetic data for portfolio demonstration. Use the sidebar to navigate.
    </p>
    """,
    unsafe_allow_html=True,
)
