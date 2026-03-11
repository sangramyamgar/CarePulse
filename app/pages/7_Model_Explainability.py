"""
Model Explainability — Interpretable readmission risk model analysis.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics import roc_curve, confusion_matrix

from app.theme import (
    page_header, insight, section, metric_row,
    COLORS, PALETTE_SEQ, empty_state,
)
from src.analysis.risk_model import train_readmission_model, FEATURE_COLUMNS

st.set_page_config(page_title="Model Explainability", page_icon="🧠", layout="wide")
page_header(
    "Model Explainability",
    "Logistic regression for 30-day readmission risk — fully interpretable",
    icon="🧠",
)

# ── Disclaimer ────────────────────────────────────────────────────────────
st.markdown(
    '<div class="insight-box">'
    "⚠️ <b>Prototype only</b> — trained on synthetic data. "
    "Not validated for clinical use. Shown to demonstrate interpretable ML thinking."
    "</div>",
    unsafe_allow_html=True,
)

# ── Train the model (cached) ─────────────────────────────────────────────
@st.cache_resource(show_spinner="Training model …")
def _train():
    return train_readmission_model()

results = _train()

if "error" in results:
    empty_state(results["error"])
    st.stop()

model = results["model"]
scaler = results["scaler"]
feat_imp = results["feature_importance"]
metrics = results["metrics"]
X_test = results["X_test"]
y_test = results["y_test"]
y_prob = results["y_prob"]

# ── Key Metrics ───────────────────────────────────────────────────────────
section("Model Performance")
metric_row([
    {"label": "AUC-ROC", "value": f"{metrics['auc']:.3f}"},
    {"label": "Accuracy", "value": f"{metrics['accuracy']:.1%}"},
    {"label": "Train Size", "value": f"{metrics['n_train']:,}"},
    {"label": "Test Size", "value": f"{metrics['n_test']:,}"},
])

insight(
    f"Readmission prevalence: {metrics['readmit_rate_train']}% in training, "
    f"{metrics['readmit_rate_test']}% in test. "
    "AUC > 0.65 on synthetic data indicates the features carry real signal."
)

# ── ROC Curve + Feature Importance side-by-side ──────────────────────────
section("ROC Curve & Feature Importance")
col_roc, col_feat = st.columns(2)

with col_roc:
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    fig_roc = go.Figure()
    fig_roc.add_trace(go.Scatter(
        x=fpr, y=tpr,
        mode="lines",
        line=dict(color=COLORS["primary"], width=2.5),
        name=f"AUC = {metrics['auc']:.3f}",
        fill="tozeroy",
        fillcolor="rgba(0,87,184,0.08)",
    ))
    fig_roc.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        mode="lines",
        line=dict(dash="dash", color=COLORS["text_muted"], width=1),
        showlegend=False,
    ))
    fig_roc.update_layout(
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate",
        height=380,
        legend=dict(x=0.55, y=0.1),
    )
    st.plotly_chart(fig_roc, use_container_width=True)

with col_feat:
    fig_feat = px.bar(
        feat_imp, y="feature", x="coefficient", orientation="h",
        color="coefficient",
        color_continuous_scale=["#10B981", "#F1F5F9", "#EF4444"],
        color_continuous_midpoint=0,
        labels={"feature": "", "coefficient": "Coefficient (scaled)"},
    )
    fig_feat.update_layout(
        yaxis=dict(categoryorder="total ascending"),
        coloraxis_showscale=False,
        height=380,
    )
    st.plotly_chart(fig_feat, use_container_width=True)

insight(
    "Positive coefficients increase readmission risk. "
    "Chronic condition count and LOS are typically the strongest drivers — "
    "this aligns with published clinical research."
)

# ── Confusion Matrix ─────────────────────────────────────────────────────
section("Confusion Matrix")
y_pred = model.predict(scaler.transform(X_test))
cm = confusion_matrix(y_test, y_pred)
labels = ["No Readmit", "Readmit"]

fig_cm = go.Figure(data=go.Heatmap(
    z=cm[::-1],
    x=labels,
    y=labels[::-1],
    text=cm[::-1],
    texttemplate="%{text:,}",
    colorscale=[[0, "#EFF6FF"], [1, COLORS["primary"]]],
    showscale=False,
))
fig_cm.update_layout(
    xaxis_title="Predicted", yaxis_title="Actual",
    height=340, width=400,
)
st.plotly_chart(fig_cm, use_container_width=True)

# ── Classification Report ────────────────────────────────────────────────
section("Classification Report")
report = metrics["report"]
report_rows = []
for label_key in ["0", "1"]:
    if label_key in report:
        row = report[label_key]
        report_rows.append({
            "Class": "No Readmit" if label_key == "0" else "Readmit",
            "Precision": f"{row['precision']:.3f}",
            "Recall": f"{row['recall']:.3f}",
            "F1-Score": f"{row['f1-score']:.3f}",
            "Support": int(row["support"]),
        })
if report_rows:
    st.dataframe(pd.DataFrame(report_rows), use_container_width=True, hide_index=True)

# ── Interactive Risk Scorer ──────────────────────────────────────────────
st.markdown("---")
section("Interactive Risk Scorer")
st.markdown("Adjust patient features to see predicted readmission probability.")

sc1, sc2, sc3, sc4 = st.columns(4)
with sc1:
    age_val = st.slider("Age", 18, 90, 55, key="scorer_age")
with sc2:
    chronic_val = st.slider("Chronic Conditions", 0, 12, 3, key="scorer_chronic")
with sc3:
    los_val = st.slider("LOS (days)", 0, 30, 5, key="scorer_los")
with sc4:
    cost_val = st.slider("Total Cost ($K)", 0, 200, 25, key="scorer_cost")

sc5, sc6, sc7, sc8 = st.columns(4)
with sc5:
    gender_val = st.selectbox("Gender", ["Male", "Female"], key="scorer_gender")
with sc6:
    month_val = st.slider("Encounter Month", 1, 12, 6, key="scorer_month")
with sc7:
    prior_inp = st.slider("Prior Inpatient (12 mo)", 0, 10, 1, key="scorer_prior")
with sc8:
    ed_prior = st.selectbox("ED Visit ≤30d", ["No", "Yes"], key="scorer_ed")

input_vals = np.array([[
    age_val,
    1 if gender_val == "Male" else 0,
    chronic_val,
    los_val,
    cost_val * 1000,
    month_val,
    prior_inp,
    1 if ed_prior == "Yes" else 0,
]])
prob = model.predict_proba(scaler.transform(input_vals))[0][1]

prob_color = COLORS["secondary"] if prob < 0.3 else (COLORS["accent"] if prob < 0.6 else COLORS["danger"])
st.markdown(
    f"<div style='text-align:center; padding:20px; background:#F8FAFC; "
    f"border-radius:12px; border:1px solid #E2E8F0;'>"
    f"<span style='font-size:0.85rem; color:#64748B; text-transform:uppercase; "
    f"letter-spacing:0.05em;'>Predicted Readmission Probability</span><br>"
    f"<span style='font-size:2.5rem; font-weight:700; color:{prob_color};'>"
    f"{prob:.1%}</span></div>",
    unsafe_allow_html=True,
)

insight(
    "This scorer shows how feature changes affect the prediction. "
    "In a real system, this would be embedded in EHR workflows for discharge planning."
)
