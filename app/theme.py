"""
CarePulse Design System — shared theme, layout helpers, and Plotly defaults.

Import this at the top of every dashboard page for consistent styling.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio

# ---------------------------------------------------------------------------
# Color palette — Kaiser-inspired healthcare blue + warm accents
# ---------------------------------------------------------------------------
COLORS = {
    "primary": "#0057B8",       # Deep Kaiser blue
    "primary_light": "#3B82F6",
    "primary_muted": "#93C5FD",
    "secondary": "#10B981",     # Teal green
    "accent": "#F59E0B",        # Warm amber
    "danger": "#EF4444",        # Red for alerts
    "danger_light": "#FCA5A5",
    "text": "#1E293B",          # Slate-800
    "text_muted": "#64748B",    # Slate-500
    "bg_card": "#F8FAFC",       # Slate-50
    "border": "#E2E8F0",        # Slate-200
    "white": "#FFFFFF",
}

PALETTE_SEQ = [
    "#0057B8", "#10B981", "#F59E0B", "#EF4444",
    "#8B5CF6", "#EC4899", "#14B8A6", "#F97316",
]

PALETTE_DIVERGE = ["#10B981", "#F59E0B", "#EF4444"]  # good → mid → bad

# ---------------------------------------------------------------------------
# Plotly template
# ---------------------------------------------------------------------------
_cp_template = go.layout.Template()
_cp_template.layout = go.Layout(
    font=dict(family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", size=13, color=COLORS["text"]),
    paper_bgcolor=COLORS["white"],
    plot_bgcolor=COLORS["white"],
    colorway=PALETTE_SEQ,
    title=dict(font=dict(size=16, color=COLORS["text"]), x=0, xanchor="left"),
    xaxis=dict(gridcolor="#F1F5F9", linecolor=COLORS["border"], zeroline=False),
    yaxis=dict(gridcolor="#F1F5F9", linecolor=COLORS["border"], zeroline=False),
    margin=dict(l=40, r=24, t=48, b=40),
    hoverlabel=dict(bgcolor=COLORS["white"], font_size=12, bordercolor=COLORS["border"]),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
    bargap=0.25,
)
pio.templates["carepulse"] = _cp_template
pio.templates.default = "carepulse"

# ---------------------------------------------------------------------------
# Custom CSS injected once per page
# ---------------------------------------------------------------------------
_CSS = """
<style>
/* Import Inter font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Global reset */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Hide Streamlit default header and footer */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0057B8 0%, #003D82 100%);
    padding-top: 1rem;
}
[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stDateInput label {
    color: #93C5FD !important;
    font-weight: 500;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Date input: keep text dark inside the white input box */
[data-testid="stSidebar"] .stDateInput input {
    color: #1E293B !important;
    background: #FFFFFF !important;
}
[data-testid="stSidebar"] .stDateInput [data-baseweb="input"] {
    background: #FFFFFF !important;
}
[data-testid="stSidebar"] .stDateInput svg {
    fill: #64748B !important;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
[data-testid="stMetric"] label {
    color: #64748B !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #0057B8 !important;
    font-size: 1.75rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetric"] [data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 2px solid #E2E8F0;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    padding: 8px 20px;
    font-weight: 500;
    color: #64748B;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: #EFF6FF;
    color: #0057B8;
    border-bottom: 3px solid #0057B8;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    overflow: hidden;
}

/* Download buttons */
.stDownloadButton > button {
    background: transparent !important;
    border: 1px solid #E2E8F0 !important;
    color: #64748B !important;
    font-size: 0.78rem !important;
    padding: 4px 12px !important;
    border-radius: 6px !important;
}
.stDownloadButton > button:hover {
    border-color: #0057B8 !important;
    color: #0057B8 !important;
}

/* Smooth divider */
hr {
    border: none;
    height: 1px;
    background: #E2E8F0;
    margin: 1.5rem 0;
}

/* Section headers */
h2, h3 {
    color: #1E293B !important;
    font-weight: 600 !important;
}

/* Caption / insight text */
.insight-box {
    background: #EFF6FF;
    border-left: 4px solid #0057B8;
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    margin: 8px 0 16px 0;
    font-size: 0.88rem;
    color: #334155;
    line-height: 1.5;
}
</style>
"""


def inject_css():
    """Call once at the top of each page to apply the CarePulse theme."""
    st.markdown(_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = ""):
    """Render a consistent page header."""
    inject_css()
    if icon:
        st.markdown(f"<h1 style='margin-bottom:0; color:#0057B8; font-size:2rem;'>{icon} {title}</h1>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h1 style='margin-bottom:0; color:#0057B8; font-size:2rem;'>{title}</h1>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<p style='color:#64748B; margin-top:4px; font-size:1rem;'>{subtitle}</p>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)


def insight(text: str):
    """Render an insight callout box (replaces st.caption for 'So what?' notes)."""
    st.markdown(f'<div class="insight-box">💡 {text}</div>', unsafe_allow_html=True)


def section(title: str):
    """Render a section divider."""
    st.markdown(f"<h3 style='margin-top:1.5rem;'>{title}</h3>", unsafe_allow_html=True)


def metric_row(data: list[dict]):
    """
    Render a row of metric cards.
    data: list of dicts with keys 'label', 'value', and optional 'delta'.
    """
    cols = st.columns(len(data))
    for col, d in zip(cols, data):
        col.metric(d["label"], d["value"], delta=d.get("delta"))


def empty_state(message: str = "No data available."):
    """Render a friendly empty state."""
    st.markdown(
        f"<div style='text-align:center; padding:40px; color:#94A3B8;'>"
        f"<p style='font-size:2rem;'>📭</p>"
        f"<p>{message}</p></div>",
        unsafe_allow_html=True,
    )
