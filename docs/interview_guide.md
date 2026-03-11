# CarePulse — Interview Guide

A comprehensive guide to explaining every aspect of this project in interviews.

---

## Table of Contents

1. [Elevator Pitches (30s / 1m / 2m / 5m)](#elevator-pitches)
2. [Problem Statement in Simple Words](#problem-statement)
3. [Why This Project Matters in Healthcare](#why-it-matters)
4. [Architecture Explanation](#architecture)
5. [Database / Schema Explanation](#database)
6. [Why PostgreSQL](#why-postgresql)
7. [Why Streamlit](#why-streamlit)
8. [Why SQL in Separate Files](#why-separate-sql)
9. [Major Design Choices and Tradeoffs](#design-choices)
10. [All Assumptions](#assumptions)
11. [Limitations of Synthetic Data](#synthetic-data-limitations)
12. [How to Explain the Dashboard](#explaining-the-dashboard)
13. [How to Explain the Model](#explaining-the-model)
14. [Common Interview Questions and Answers](#interview-questions)
15. [Explain to Different Audiences](#different-audiences)
16. [Glossary](#glossary)

---

## Elevator Pitches

### 30-Second Version

> "I built CarePulse, a healthcare analytics platform that analyzes patient readmission patterns, hospital utilization, and HEDIS quality measures. It takes synthetic patient data, runs it through a Python ETL into PostgreSQL, applies dbt transformations, and presents everything through an 8-page interactive Streamlit dashboard. It includes an interpretable ML risk model, NCQA-aligned HEDIS measures, and a full CI pipeline with GitHub Actions. The goal is to help hospital leadership identify which patient groups are coming back too soon and where operational hotspots exist."

### 1-Minute Version

> "CarePulse is a healthcare analytics project I built end-to-end. It simulates realistic hospital data — patients, encounters, conditions, medications — and loads it into a PostgreSQL database with a normalized relational schema. I wrote SQL analytics using CTEs and window functions to compute 30-day readmission rates, average length of stay, and utilization trends. I added dbt for transformation management (staging + mart models with 27 tests), HEDIS-style quality measures (ACR and FUH), and an interpretable logistic regression model with an interactive risk scorer. The results are surfaced through an 8-page Streamlit dashboard with KPI cards, interactive Plotly charts, cohort breakdowns, facility comparisons, a model explainability page, and HEDIS reporting. There's also a GitHub Actions CI pipeline, global date filters, CSV exports, and a data quality monitoring page. The architecture: CSV → Python ETL → PostgreSQL → dbt → SQL analytics → Dashboard. Every piece is explainable and locally runnable."

### 2-Minute Version

> Start with the 1-minute version, then add:
>
> "The project answers questions a hospital VP would actually ask: Which age groups have the highest readmission rates? Are patients with multiple chronic conditions returning more often? How do our facilities compare on cost and length of stay? I used a Synthea-style data generator to create 1,000 patients with ~6,000 encounters across 8 facilities. The readmission detection uses a LEAD window function to find the next inpatient admission per patient, then flags any gaps of 30 days or less. I built dbt models (3 staging + 3 mart) with 27 tests for transformation management. I implemented HEDIS measures — ACR (All-Cause Readmissions) and FUH (Follow-Up After MH Hospitalization) — to demonstrate NCQA-aligned quality reporting. The model explainability page shows ROC curves, feature importance, a confusion matrix, and an interactive risk scorer. I chose this architecture because it mirrors real-world healthcare analytics: a data warehouse, dbt transformations, SQL-based reporting, HEDIS measures, and a BI-style dashboard — just scaled down to be portfolio-appropriate."

### 5-Minute Version

> Use the 2-minute version as a foundation. Then walk through:
>
> 1. **The data model** — show the ER diagram, explain patients → encounters → conditions/procedures/medications
> 2. **One SQL query** — open readmission_flag.sql and explain the CTE + LEAD window function
> 3. **The dashboard** — demo the Executive Overview (KPI cards, monthly trend) and Readmission Analysis (cohort breakdowns)
> 4. **dbt** — show the staging → mart model chain, explain the 27 automated tests
> 5. **HEDIS Measures** — explain ACR/FUH measures and NCQA alignment
> 6. **Model Explainability** — show ROC curve, feature importance, interactive risk scorer
> 7. **Data quality** — show the quality score gauge and explain why you built monitoring
> 8. **What you'd improve** — mention time-based train/test split, clinical validation, Airflow for scheduling, more HEDIS measures

---

## Problem Statement

Hospitals need to reduce 30-day readmissions because:
- **Patient safety** — readmissions often mean something went wrong in care or discharge
- **Financial penalties** — CMS (Centers for Medicare & Medicaid Services) penalizes hospitals with excess readmission rates through the Hospital Readmissions Reduction Program (HRRP)
- **Operational efficiency** — readmissions consume bed capacity that could serve new patients

CarePulse helps hospital analysts and leadership **see** where readmissions are happening, **understand** which patient groups are most affected, and **act** on data-driven insights.

---

## Why This Project Matters in Healthcare

- **30-day readmission** is one of the most tracked quality metrics in US healthcare
- CMS financially penalizes hospitals — this is a real dollar impact
- Reducing readmissions improves patient outcomes AND saves money
- Data analytics is how hospitals identify the root causes
- This project demonstrates the exact workflow a healthcare analyst does daily

---

## Architecture

```
Synthea-style CSVs → Python ETL (pandas) → PostgreSQL → SQL Analytics → Streamlit Dashboard
```

**Why this architecture?**
- It mirrors a real healthcare data warehouse pipeline
- Each layer has a clear responsibility
- You can test and debug each layer independently
- SQL stays visible and reviewable (not buried in Python)

**What this project already includes (beyond a typical portfolio project):**
- **dbt** for transformation management (3 staging + 3 mart models, 27 tests)
- **GitHub Actions CI** pipeline (pytest + dbt build against PostgreSQL service)
- **HEDIS quality measures** (NCQA-aligned ACR and FUH)
- **Model explainability** page with interactive risk scorer
- **Data lineage** diagram (Mermaid) in architecture docs

**What a production version would add:**
- Airflow for scheduling the ETL pipeline
- A proper data warehouse (Snowflake, Redshift)
- Role-based access control
- More HEDIS measures (BCS, CIS, CDC)

---

## Database

The schema has 8 tables:
- **patients** — demographic info (birth date, gender, race, location)
- **encounters** — every visit/admission (type, dates, cost, payer)
- **conditions** — diagnoses linked to encounters (SNOMED codes)
- **procedures** — clinical procedures performed
- **medications** — prescriptions with start/stop dates
- **providers** — doctors with specialties
- **organizations** — hospitals/facilities
- **readmissions** — derived analytic table (built by ETL, not raw data)

Key relationships:
- `patients` → `encounters` (one-to-many)
- `encounters` → `conditions/procedures/medications` (one-to-many)
- `encounters` → `providers` and `organizations` (many-to-one)

---

## Why PostgreSQL

**What to say:**
> "I chose PostgreSQL because it's the most widely used open-source relational database in healthcare analytics. It supports window functions, CTEs, and date arithmetic natively — all critical for readmission logic. It also mirrors what I'd use in a real data warehouse. SQLite would have been simpler to set up, but it lacks window function performance and doesn't demonstrate production-relevant skills."

**If asked "why not SQLite?":**
> "SQLite is great for prototyping, but PostgreSQL shows I can work with a real database server, which is what healthcare organizations actually use."

---

## Why Streamlit

**What to say:**
> "Streamlit lets me build a real interactive dashboard in Python without learning JavaScript or a full frontend framework. It's the closest thing to a BI tool that I can code from scratch. The multi-page layout gives it a professional feel, and Plotly charts make it interactive."

**If asked "why not Tableau/Power BI?":**
> "Those are great tools, but building the dashboard in code demonstrates deeper technical skills. In an interview, I can walk through every line. I can also show how the dashboard connects directly to the database and SQL queries."

---

## Why SQL in Separate Files

**What to say:**
> "I separated SQL into .sql files for three reasons:
> 1. **Review** — an interviewer or colleague can read the SQL without running Python
> 2. **Reusability** — the same query could be run in a SQL client, dbt, or another tool
> 3. **Skill demonstration** — it proves I write real SQL, not just pandas .groupby()"

---

## Design Choices and Tradeoffs

| Decision | Alternative Considered | Why I Chose This |
|----------|----------------------|------------------|
| Synthetic data generator | Download full Synthea | Simpler setup, reproducible, no Java needed |
| pandas for ETL | Raw SQL COPY | pandas gives me cleaning/validation flexibility |
| SQLAlchemy text() | Full ORM | Transparent SQL, no ORM magic to explain |
| Streamlit multi-page | Single long page | Professional layout, focused analysis per page |
| Logistic regression | Random forest, XGBoost | Fully interpretable, coefficients make sense |
| No Docker | Docker Compose | Unnecessary complexity for a local portfolio project |
| No Airflow | Airflow DAGs | Overkill — I'd mention it as a production improvement |

---

## Assumptions

1. "Inpatient" encounters are the index events for readmission logic
2. 30-day window is measured from discharge to next admission start
3. Same-day discharges (LOS = 0) are valid for outpatient/ED
4. All conditions without a resolved_date are treated as "chronic"
5. Synthetic data distributions approximate US healthcare patterns but are not clinically accurate
6. Encounters are independent (no transfer logic between facilities)

---

## Limitations of Synthetic Data

**What to say:**
> "The data is generated by a Python script, not from real patients. This means:
> - The distributions are approximate, not clinically validated
> - Correlations between conditions and outcomes are random, not medically accurate
> - The model coefficients are illustrative, not predictive in a real setting
> - However, the **methodology** is exactly what you'd apply to real data
> - I chose synthetic data to avoid any HIPAA concerns and ensure full reproducibility"

---

## Explaining the Dashboard

Walk through each page:

1. **Home** — explains what the platform does and how to navigate all 8 pages
2. **Executive Overview** — "These are the numbers a hospital CEO sees on Monday morning: total encounters, readmission rate, average LOS, cost. The monthly trend shows if things are getting better or worse. Global date filters let you drill into any time range."
3. **Cohort Explorer** — "This breaks down our patient population by age, gender, race, and chronic-condition burden. The key insight is patients with 3+ chronic conditions — they drive disproportionate resource use."
4. **Readmission Analysis** — "This is the heart of the project. We can slice readmission rates by age, condition, payer, and chronic count. Each chart has a 'so what?' annotation explaining what the pattern means."
5. **Utilization Trends** — "Volume and cost trends over time. If total cost is rising but average cost is flat, it means we're seeing more patients, not sicker patients."
6. **Facility Drilldown** — "Compares our 8 facilities on readmission rate, cost, and length of stay. Uses NTILE quartile rankings to identify outliers."
7. **Data Quality** — "Before trusting any dashboard, you need to know if your data is clean. This page scores completeness, uniqueness, and referential integrity."
8. **Model Explainability** — "Shows the logistic regression model's ROC curve, feature importance, confusion matrix, and an interactive risk scorer where you can adjust patient features with sliders and see the predicted probability change in real time."
9. **HEDIS Measures** — "NCQA-aligned quality measures. ACR (All-Cause Readmissions) shows readmission rates for adults 18-64 with quarterly trends and payer breakdowns. FUH tracks follow-up after mental health hospitalization. Includes measure definition reference tables."

---

## Explaining the Model

**What to say:**
> "I added a simple logistic regression model — not as a clinical prediction tool, but to identify which factors are most associated with readmission. The features are: age, gender, chronic condition count, length of stay, cost, prior inpatient visits, and recent ED visits. The model is fully interpretable — I can show you the coefficients. For example, chronic_count having a positive coefficient means more chronic conditions increase readmission risk, which aligns with clinical intuition."

**Key points to emphasize:**
- This is a **prototype**, not a production model
- Synthetic data means coefficients aren't clinically valid
- A real model would need temporal train/test splits, bias auditing, and clinical review
- I chose logistic regression specifically because it's interpretable

---

## Common Interview Questions and Answers

### "What would you improve in production?"

> "Several things:
> 1. **Airflow** to schedule the ETL pipeline on a daily/weekly cadence
> 2. **Time-based train/test split** for the model (don't train on future data)
> 3. **Role-based access** so clinicians see only their facility's data
> 4. **Alerting** — notify when readmission rate exceeds a threshold
> 5. **Proper data warehouse** (Snowflake/Redshift) for larger data
> 6. **More HEDIS measures** — BCS, CIS, CDC for pediatric and preventive care
> 7. **Patient-level drilldown** — click a row to see individual encounter history"
>
> Note: dbt, CI/CD, data lineage, and model explainability are already implemented in this project.

### "Why didn't you use deep learning?"

> "Deep learning would be inappropriate here. First, readmission prediction doesn't need neural networks — logistic regression achieves comparable AUC on most published benchmarks. Second, interpretability is critical in healthcare: a hospital administrator needs to understand WHY a patient is flagged as high-risk, not just that they are. Third, the dataset is small enough that deep learning would overfit. Finally, CMS and regulators require explainable models for clinical decision support."

### "What part was hardest?"

> "Two things were challenging:
> 1. **Getting the readmission logic right** — making sure the window function correctly identifies the NEXT admission (not any future admission), handling patients with only one encounter, and dealing with date edge cases.
> 2. **Balancing polish vs. complexity** — I wanted the dashboard to look professional without adding so many features that I couldn't explain it. I cut several ideas (patient-level drilldown, medication adherence tracking) to keep the project focused."

### "How did you ensure data quality?"

> "Three layers:
> 1. **At ingestion** — the cleaning script removes duplicates, fixes date inconsistencies, and validates required fields
> 2. **At query time** — SQL queries use NULLIF and COALESCE to handle edge cases gracefully
> 3. **Data Quality Monitor** — a dedicated dashboard page that computes completeness, uniqueness, and referential integrity scores. This is something I'd run after every data refresh in production."

### "How does the readmission logic work?"

> "I sort all inpatient encounters per patient by date, then use a LEAD window function to look at the next admission. The gap between the current discharge date and the next start date gives days_to_readmit. If that's ≤ 30, I flag it. In the Python ETL, I do the same thing with pandas shift(). Both approaches give the same result — I implemented both to demonstrate SQL and Python proficiency."

### "What's a CTE and why did you use it?"

> "CTE stands for Common Table Expression — it's like a named subquery that makes SQL more readable. Instead of nesting subqueries three levels deep, I break the logic into steps: first filter to inpatient, then apply the window function, then calculate days. Each step has a clear name, making the query self-documenting."

### "How would you handle real data?"

> "The methodology stays the same. The main changes would be:
> - Data comes from an EHR system or claims database instead of CSVs
> - HIPAA compliance: data access controls, audit logging, de-identification
> - More complex encounter logic (transfers, observation stays)
> - Clinical validation of condition groupings
> - Much larger data volume → would use a columnar warehouse"

---

## Interviewer Traps and How to Avoid Sounding Fake

### Trap: "Did you build this from scratch?"

**Don't say:** "Yes, completely from scratch with no help."
**Do say:** "I designed the architecture and wrote all the code. I referenced documentation and best practices for SQL patterns and Streamlit layout. The data model is inspired by Synthea's standard healthcare data format."

### Trap: "What's the AUC of your model?"

**Don't say:** Just rattle off a number.
**Do say:** "The AUC is [number], but I want to caveat that this is on synthetic data. The real value of the model is showing which features matter — age, chronic count, and prior utilization — which aligns with published clinical research."

### Trap: "Why didn't you use [some complex tool]?"

**Don't say:** "I don't know that tool."
**Do say:** "I evaluated the tradeoffs and chose [simpler tool] because it meets the requirements without adding complexity that would be hard to maintain. In production, I'd consider [complex tool] when [specific condition is met]."

### Trap: "How is this different from a Kaggle project?"

**Do say:** "This isn't a modeling exercise. It's an analytics platform. The output isn't a prediction — it's dashboards, metrics, and business insights. The SQL, data modeling, and data quality work are what make it realistic. A Kaggle project would skip all of that and jump to model accuracy."

---

## Explain This Like I'm a Non-Technical Manager

> "CarePulse is a dashboard tool that helps hospitals understand their patient data. It answers questions like: 'How many patients come back within a month of leaving?' and 'Which of our hospitals has the highest readmission rate?' Think of it like a health check for the hospital itself. I built it using a real database, professional-grade charts, and quality checks to make sure the numbers are trustworthy."

---

## Explain This Like I'm a Data Engineer

> "It's a batch ETL pipeline: Python generates Synthea-style CSVs, loads them into PostgreSQL with pandas + SQLAlchemy, runs cleaning passes (dedup, date validation, null checks), then builds a derived readmissions table using a window function self-join on the encounters table. dbt manages the transformation layer — 3 staging models + 3 mart models with 27 tests. SQL analytics queries live in separate .sql files — CTEs, LEAD(), PERCENTILE_CONT, DATE_TRUNC aggregations, plus HEDIS measure definitions (ACR, FUH). The Streamlit app reads from Postgres via the same SQLAlchemy engine. GitHub Actions CI runs pytest + dbt build against a PostgreSQL service container. Tests cover transformation logic, readmission flagging, and DQ checks. In production, I'd add Airflow scheduling and a proper warehouse."

---

## Explain This Like I'm a Data Analyst Lead

> "CarePulse is a self-contained analytics platform focused on 30-day readmission, utilization, and HEDIS quality measures. The data model has 7 base tables (patients, encounters, conditions, procedures, medications, providers, organizations) plus a derived readmissions table. dbt adds 3 staging + 3 mart models. Key metrics: 30-day readmission rate, ALOS, ED utilization, chronic burden, HEDIS ACR (All-Cause Readmissions), and HEDIS FUH. The dashboard has 8 pages: exec overview, cohort explorer, readmission deep-dive, utilization trends, facility drilldown, data quality, model explainability (with interactive risk scorer), and HEDIS measures. Every chart has a 'so what' annotation. SQL is in separate files for reviewability. A logistic regression risk score is positioned as decision-support with full explainability — ROC curve, feature importance, confusion matrix. CI runs on GitHub Actions."

---

## Glossary

| Term | Definition |
|------|-----------|
| **30-Day Readmission** | A patient who is discharged from an inpatient stay and returns for another inpatient stay within 30 calendar days |
| **ALOS (Average Length of Stay)** | Mean number of days for inpatient encounters from admission to discharge |
| **CMS** | Centers for Medicare & Medicaid Services — the US federal agency that administers Medicare |
| **CTE (Common Table Expression)** | A named subquery in SQL that improves readability |
| **Encounter** | A single patient visit or admission event (inpatient, outpatient, emergency, etc.) |
| **Encounter Class** | The type of visit: inpatient, outpatient, emergency, wellness, ambulatory |
| **ETL** | Extract, Transform, Load — the process of moving data from source to analytics-ready |
| **FK (Foreign Key)** | A column that references the primary key of another table |
| **HRRP** | Hospital Readmissions Reduction Program — CMS program that penalizes hospitals for excess readmissions |
| **LOS** | Length of Stay — how many days a patient stays in the hospital |
| **Payer** | The insurance provider paying for the encounter (Medicare, Medicaid, private insurance, etc.) |
| **PK (Primary Key)** | A column that uniquely identifies each row in a table |
| **SNOMED** | A standardized clinical terminology system for conditions and procedures |
| **SQLAlchemy** | A Python library that provides a connection layer to databases |
| **Streamlit** | A Python framework for building interactive web dashboards |
| **Synthea** | An open-source tool that generates realistic synthetic patient records |
| **Window Function** | A SQL function that performs a calculation across a set of rows related to the current row (e.g., LEAD, LAG, ROW_NUMBER) |
| **dbt** | Data Build Tool — a transformation framework for SQL-based data warehouses |
| **Plotly** | A Python visualization library for interactive charts |
