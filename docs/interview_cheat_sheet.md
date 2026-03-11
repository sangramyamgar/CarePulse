# CarePulse — Interview Cheat Sheet

Quick-reference card for revision the night before the interview.

---

## Ultra-Short Talking Points

- **What:** End-to-end healthcare analytics platform for readmission, utilization, and HEDIS quality measure analysis
- **Data:** Synthetic (Synthea-style), 1,000 patients, ~6,000 encounters, 8 facilities
- **Stack:** Python + pandas + PostgreSQL + SQL + dbt + Streamlit + Plotly + scikit-learn
- **Core metric:** 30-day all-cause readmission rate
- **Dashboard:** 8 pages — Exec Overview, Cohorts, Readmissions, Utilization, Facilities, Data Quality, Model Explainability, HEDIS Measures
- **Model:** Logistic regression (interpretable, interactive risk scorer, ROC + feature importance)
- **dbt:** 3 staging + 3 mart models, 27 automated tests
- **HEDIS:** ACR (All-Cause Readmissions) and FUH (Follow-Up After MH Hospitalization)
- **CI/CD:** GitHub Actions with PostgreSQL service container (pytest + dbt build)
- **Key SQL:** CTEs, LEAD() window function, DATE_TRUNC, PERCENTILE_CONT, NTILE
- **Differentiator:** Not a Kaggle project — it's an analytics product with dbt, CI, HEDIS, model explainability, data lineage, and business storytelling

---

## 20 Likely Interview Questions with Compact Answers

### 1. "Walk me through the project."
→ Use the 1-minute elevator pitch. Start with the problem (readmissions), then the pipeline (CSV → Postgres → SQL → Dashboard), then one key insight.

### 2. "Why readmissions?"
→ It's a CMS-tracked quality metric. Hospitals get financially penalized. It's the #1 healthcare analytics use case.

### 3. "Explain your data model."
→ 7 base tables centered on patients and encounters. Conditions, procedures, and medications link to encounters. A derived readmissions table powers the analytics.

### 4. "How did you calculate readmission rate?"
→ Filter to inpatient encounters. For each patient, use LEAD() to find the next admission. If the gap between discharge and next admission is ≤ 30 days, flag it.

### 5. "What's a window function?"
→ A SQL function that calculates across related rows without collapsing them. LEAD() looks at the next row in a group. I partitioned by patient_id, ordered by date.

### 6. "Why PostgreSQL over SQLite?"
→ Window functions, date math, production relevance. SQLite is fine for prototyping but doesn't demonstrate enterprise skills.

### 7. "Why Streamlit over Tableau?"
→ Code-based = I can explain every detail. Also shows Python proficiency. In practice, I'd use both.

### 8. "How did you handle data quality?"
→ Three layers: ingestion cleaning (dedup, date fixes), SQL edge-case handling (NULLIF, COALESCE), dedicated DQ dashboard with automated scoring.

### 9. "What would you change for production?"
→ Airflow for scheduling, proper warehouse (Snowflake), RBAC, alerting, more HEDIS measures. Note: dbt, CI/CD, data lineage, and model explainability are already built.

### 10. "Why not deep learning?"
→ Doesn't outperform logistic regression for tabular readmission data. Not interpretable. Regulators require explainability.

### 11. "What was the hardest part?"
→ Getting readmission logic right (edge cases with single encounters, same-day readmits). Balancing polish with explainability.

### 12. "Is the model clinically valid?"
→ No — it's on synthetic data. The value is showing which features matter. A real model needs clinical validation, bias audit, and regulatory review.

### 13. "What's a CTE?"
→ Common Table Expression. A named subquery. Makes SQL readable by breaking complex logic into named steps.

### 14. "How does data flow end-to-end?"
→ Generate CSVs → Load into Postgres → Clean/validate → Build readmissions table → dbt staging/mart models → SQL analytics → Streamlit reads results → Charts rendered. CI runs all of this automatically on every push.

### 15. "What metrics did you track?"
→ 30-day readmission rate, ALOS, ED utilization, chronic burden, payer mix, cost trends, DQ score, HEDIS ACR (All-Cause Readmissions), HEDIS FUH (Follow-Up After MH Hospitalization).

### 16. "How is this different from a school project?"
→ Normalized schema, production-style SQL, data quality monitoring, business-relevant metrics, multi-page dashboard with storytelling. Not just a notebook.

### 17. "What assumptions did you make?"
→ Inpatient-only readmissions, 30-day window from discharge to admission, unresolved conditions = chronic, no transfer logic.

### 18. "What would you add with more time?"
→ Patient-level drilldown, medication adherence analysis, social determinants of health, predictive alerts, A/B testing for interventions, more HEDIS measures (BCS, CIS, CDC).

### 19. "How do you ensure your SQL is correct?"
→ Tested edge cases (single encounter, big gaps, boundary at 30 days). Compared Python pandas output to SQL output. DQ checks validate totals.

### 20. "Tell me about a tradeoff you made."
→ I kept the model simple (logistic regression) instead of using XGBoost because interpretability matters more than marginal accuracy in healthcare.

---

## Key Metrics and Definitions

| Metric | Definition | Why It Matters |
|--------|-----------|---------------|
| 30-Day Readmission Rate | % inpatient discharges with a return within 30 days | CMS penalty metric |
| ALOS | Avg days from admission to discharge (inpatient) | Efficiency measure |
| ED Utilization | ED visits per 1,000 patients | Access-to-care indicator |
| Chronic Burden | % patients with ≥2 chronic conditions | Cost driver |
| Data Quality Score | Average of completeness + uniqueness + integrity | Trust metric |
| HEDIS ACR | All-Cause Readmission rate for ages 18–64 | NCQA quality measure |
| HEDIS FUH-7/FUH-30 | % MH discharges with 7/30-day follow-up | Behavioral health quality |

---

## Project Strengths

- ✅ End-to-end: raw data → database → dbt models → analytics → dashboard
- ✅ Healthcare-specific metrics (readmission, ALOS, chronic burden, HEDIS)
- ✅ Real SQL proficiency (CTEs, window functions, NTILE, aggregations)
- ✅ dbt transformation layer (3 staging + 3 mart models, 27 tests)
- ✅ GitHub Actions CI pipeline (pytest + dbt build)
- ✅ HEDIS quality measures (ACR, FUH) aligned with NCQA specifications
- ✅ Interpretable ML model with interactive risk scorer
- ✅ Data lineage diagram (Mermaid in architecture docs)
- ✅ Normalized relational data model
- ✅ Data quality monitoring (not just analysis)
- ✅ Interactive 8-page dashboard with business storytelling ("so what?" annotations)
- ✅ Global date filters and CSV exports
- ✅ Clean, modular code structure
- ✅ Locally runnable on macOS
- ✅ Fully reproducible (synthetic data)

---

## Limitations

- ⚠️ Synthetic data — patterns aren't clinically accurate
- ⚠️ No real EHR integration
- ⚠️ No scheduling/orchestration (no Airflow)
- ⚠️ Single-user local setup (no RBAC)
- ⚠️ Model is illustrative, not deployable
- ⚠️ No incremental loading (full refresh each run)
- ⚠️ No transfer/observation-stay logic
- ⚠️ FUH measure has no data in synthetic set (gracefully handled)

---

## Top 5 Things I Must Not Forget

1. **Start with the business problem** — "Hospitals get penalized for readmissions. This tool helps them find out why."
2. **Walk through the data flow** — CSV → ETL → Postgres → dbt → SQL → Dashboard. Don't skip this.
3. **Show ONE SQL query** — Open readmission_flag.sql. Explain the LEAD() window function.
4. **Mention dbt and CI** — "I have 27 dbt tests passing automatically on every push via GitHub Actions."
5. **Be honest about limitations** — "It's synthetic data. The model is illustrative. In production, I'd add Airflow and clinical validation."
