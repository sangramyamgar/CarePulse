"""
CarePulse — Home Page

This is the Streamlit entry point. It sets the overall layout
and displays a welcome screen with project overview.
"""

import streamlit as st

st.set_page_config(
    page_title="CarePulse Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏥 CarePulse")
st.subheader("Readmission & Utilization Analytics Platform")

st.markdown("---")

st.markdown("""
**CarePulse** is a healthcare analytics platform that helps hospital leadership
understand patient readmission patterns, utilization trends, and operational
performance across facilities.

### Navigate the Dashboard

Use the sidebar to explore:

| Page | What You'll Find |
|------|-----------------|
| **Executive Overview** | High-level KPIs: readmission rate, volume, ALOS, cost |
| **Cohort Explorer** | Patient demographics, age groups, chronic-condition burden |
| **Readmission Analysis** | Deep-dive into 30-day readmission patterns and drivers |
| **Utilization Trends** | Monthly volume, service-line mix, cost trends |
| **Facility Drilldown** | Facility-by-facility comparison on key metrics |
| **Data Quality** | Data completeness, validity, and overall quality score |

### Key Metrics

- **30-Day Readmission Rate** — % of inpatient discharges followed by re-admission within 30 days
- **Average Length of Stay (ALOS)** — Mean inpatient stay duration in days
- **ED Utilization** — Emergency department visit patterns
- **Chronic Burden** — Multi-condition patient prevalence

---
*Built with synthetic data for portfolio demonstration purposes.*
""")
