"""
Readmission Risk Scoring Model (Optional)

A simple logistic regression model that predicts 30-day readmission risk.
This is included ONLY because:
  1. It genuinely adds value — it identifies which features drive readmission
  2. Logistic regression is fully interpretable
  3. It demonstrates data-to-insight thinking

IMPORTANT LIMITATIONS (for interviews):
  - This is a decision-support prototype, NOT a clinical tool
  - Synthetic data means coefficients are not clinically valid
  - A real model would need proper train/test splits across time, 
    clinical validation, bias auditing, and regulatory review
  - We use this to show "what factors matter," not to make predictions
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import StandardScaler
from src.features.build_features import build_readmission_features


# The features we use — each one is explainable in an interview
FEATURE_COLUMNS = [
    "age_at_encounter",
    "is_male",
    "chronic_count",
    "los_days",
    "total_cost",
    "encounter_month",
    "prior_inpatient_count",
    "is_emergency_prior_30d",
]

TARGET = "is_30day_readmit"


def train_readmission_model() -> dict:
    """
    Train a logistic regression model and return results.

    Returns a dictionary with:
      - model: the fitted LogisticRegression object
      - scaler: the fitted StandardScaler
      - feature_importance: DataFrame of features and their coefficients
      - metrics: dict with AUC, accuracy, and classification report
      - X_test, y_test: test data for further analysis
    """

    # Build features from the database
    df = build_readmission_features()

    if df.empty or df[TARGET].sum() == 0:
        return {"error": "Not enough data or no readmissions found"}

    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET].astype(int)

    # Train/test split (80/20, stratified to handle class imbalance)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scale features (logistic regression benefits from scaling)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train logistic regression
    # class_weight='balanced' handles the fact that readmissions are rare
    model = LogisticRegression(
        random_state=42,
        max_iter=1000,
        class_weight="balanced",
    )
    model.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]

    auc = round(roc_auc_score(y_test, y_prob), 3)
    accuracy = round((y_pred == y_test).mean(), 3)
    report = classification_report(y_test, y_pred, output_dict=True)

    # Feature importance (coefficients)
    feature_importance = pd.DataFrame({
        "feature": FEATURE_COLUMNS,
        "coefficient": model.coef_[0].round(4),
        "abs_importance": np.abs(model.coef_[0]).round(4),
    }).sort_values("abs_importance", ascending=False)

    return {
        "model": model,
        "scaler": scaler,
        "feature_importance": feature_importance,
        "metrics": {
            "auc": auc,
            "accuracy": accuracy,
            "report": report,
            "n_train": len(X_train),
            "n_test": len(X_test),
            "readmit_rate_train": round(y_train.mean() * 100, 1),
            "readmit_rate_test": round(y_test.mean() * 100, 1),
        },
        "X_test": X_test,
        "y_test": y_test,
        "y_prob": y_prob,
    }
