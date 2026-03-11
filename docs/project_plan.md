# CarePulse — Project Plan

## Status Tracker

| Phase | Status | Key Deliverables |
|-------|--------|-----------------|
| Phase 1 — Project Strategy | ✅ Complete | Strategy doc, business questions, KPIs, architecture |
| Phase 2 — Scaffold Repo | ✅ Complete | Folders, README, requirements, config |
| Phase 3 — Data Model + Ingestion | ✅ Complete | Schema DDL, synthetic data, ETL pipeline |
| Phase 4 — Analytics Layer | ✅ Complete | SQL queries, Python analytics functions |
| Phase 5 — Dashboard | ✅ Complete | 6-page Streamlit app |
| Phase 6 — Optional Model | ✅ Complete | Logistic regression risk score |
| Phase 7 — Testing + Quality | ✅ Complete | pytest suite (15 tests), DQ checks |
| Phase 8 — Interview Docs | ✅ Complete | Interview guide, cheat sheet |
| Phase 9 — Learning Guide | ✅ Complete | Tech-stack tutorial |
| Phase 10 — Setup Guide | ✅ Complete | macOS + VS Code guide |

## Business Questions

1. What is our 30-day all-cause readmission rate, and how does it trend monthly?
2. Which patient cohorts (age group, chronic condition, payer) have the highest readmission rates?
3. How does encounter volume and ALOS vary by service line?
4. Which facilities have the highest utilization and readmission rates?
5. What is the chronic-condition burden across our population?
6. Are there seasonal trends in ED vs. inpatient vs. outpatient visits?
7. Which providers handle the most complex cases?
8. Where are data-quality gaps?

## Key Design Decisions

- **Synthetic data over real data** — avoids HIPAA risk, fully reproducible
- **PostgreSQL over SQLite** — demonstrates real database skills; closer to production
- **SQL in separate files** — shows SQL proficiency; easy to review in interviews
- **Streamlit over Jupyter** — a real app, not a notebook; interviewers can use it
- **No Airflow/Docker/K8s** — keeps the project explainable and locally runnable
