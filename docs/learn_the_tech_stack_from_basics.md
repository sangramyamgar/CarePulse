# CarePulse — Learn the Tech Stack from Basics

A beginner-friendly guide to every technology used in this project. Written for someone who knows basic Python and basic SQL, and wants to understand this project deeply enough to explain and modify it.

---

## Table of Contents

1. [What Each Tool Does](#what-each-tool-does)
2. [Python Basics for This Repo](#python-basics)
3. [pandas Basics for This Repo](#pandas-basics)
4. [SQL Basics for This Repo](#sql-basics)
5. [PostgreSQL Basics for This Repo](#postgresql-basics)
6. [Streamlit Basics for This Repo](#streamlit-basics)
7. [Plotly Basics for This Repo](#plotly-basics)
8. [Testing Basics for This Repo](#testing-basics)
9. [dbt Basics for This Repo](#dbt-basics-for-this-repo)
10. [HEDIS Basics for This Repo](#hedis-basics-for-this-repo)
11. [GitHub Actions CI Basics](#github-actions-ci-basics)
12. [How the Files Connect](#how-files-connect)
13. [How Data Flows from Raw Input to Dashboard](#data-flow)
14. [14-Day Study Plan](#study-plan)
15. [Mini Exercises](#exercises)
16. [File Reading Order](#reading-order)
17. [Common Beginner Mistakes](#beginner-mistakes)

---

## What Each Tool Does

| Tool | What It Does in This Project |
|------|------------------------------|
| **Python** | The main programming language. Runs the ETL, analytics, tests, and dashboard. |
| **pandas** | Reads CSVs, cleans data, manipulates DataFrames. Used in ETL and analytics. |
| **PostgreSQL** | The database. Stores all patient/encounter data in tables. SQL queries run here. |
| **SQLAlchemy** | Connects Python to PostgreSQL. Sends SQL queries and receives results. |
| **dbt** | Data Build Tool. Manages SQL transformations as version-controlled models with automated tests. |
| **Streamlit** | Builds the web dashboard. Each page is a Python file that Streamlit renders. |
| **Plotly** | Creates interactive charts (bar, line, pie, gauge). Used inside Streamlit. |
| **scikit-learn** | Machine learning library. Trains the logistic regression readmission risk model. |
| **GitHub Actions** | CI/CD pipeline. Runs pytest and dbt build automatically on every push. |
| **pytest** | Runs tests to verify that your code logic is correct. |
| **python-dotenv** | Reads database credentials from a `.env` file so you don't hardcode passwords. |

---

## Python Basics for This Repo

### Concepts you need

1. **Variables and types** — strings, numbers, lists, dictionaries
2. **Functions** — `def my_function():` — most logic is organized into functions
3. **Imports** — `from src.db import run_query` — how Python loads code from other files
4. **f-strings** — `f"Found {count} rows"` — string formatting
5. **Dictionaries** — `metrics = {"rate": 15.2}` — used for KPI cards
6. **if/else** — simple conditionals
7. **for loops** — iterating over lists (used in data generation)
8. **Path objects** — `from pathlib import Path` — better than string paths

### Patterns used in this project

```python
# Function that returns a result
def get_readmission_rate():
    df = run_query("SELECT ... FROM readmissions")
    return df

# Entry point pattern
if __name__ == "__main__":
    main()  # Only runs when you execute this file directly
```

### What you DON'T need to know
- Classes and OOP (not used much)
- Decorators (only Streamlit's @st.cache_resource, used in model training)
- Async/await
- Generators

---

## pandas Basics for This Repo

### What pandas does
pandas lets you work with tabular data (like spreadsheets) in Python. The main object is a **DataFrame** — a table with rows and columns.

### Key operations used in this project

```python
import pandas as pd

# Read a CSV file
df = pd.read_csv("data/raw/patients.csv")

# Look at the first 5 rows
df.head()

# Select a column
df["gender"]

# Filter rows
inpatient = df[df["encounter_class"] == "inpatient"]

# Group and aggregate (like SQL GROUP BY)
df.groupby("encounter_class")["total_cost"].mean()

# Sort
df.sort_values("start_date")

# Handle missing values
df["cost"].fillna(0)

# Convert types
df["start_date"] = pd.to_datetime(df["start_date"])

# Create new columns
df["los_days"] = (df["end_date"] - df["start_date"]).dt.days

# Shift within groups (key for readmission logic!)
df["next_admit"] = df.groupby("patient_id")["start_date"].shift(-1)

# Write to database
df.to_sql("patients", engine, if_exists="replace", index=False)
```

### Most important pandas function in this project
`groupby().shift(-1)` — this is how we find the NEXT admission for each patient. `shift(-1)` moves the column up by one row within each group.

---

## SQL Basics for This Repo

### What SQL does
SQL (Structured Query Language) talks to the database. You use it to create tables, insert data, and — most importantly — query data.

### Key SQL patterns

```sql
-- SELECT: get data
SELECT * FROM patients;

-- WHERE: filter
SELECT * FROM encounters WHERE encounter_class = 'inpatient';

-- JOIN: combine tables
SELECT e.*, p.gender
FROM encounters e
JOIN patients p ON e.patient_id = p.id;

-- GROUP BY: aggregate
SELECT encounter_class, COUNT(*) AS total
FROM encounters
GROUP BY encounter_class;

-- ORDER BY: sort
SELECT * FROM encounters ORDER BY start_date DESC;

-- ROUND, COALESCE, NULLIF
SELECT ROUND(AVG(total_cost), 2) FROM encounters;
SELECT COALESCE(death_date, 'Still alive') FROM patients;
```

### Advanced SQL used in this project

#### CTEs (Common Table Expressions)
```sql
-- Named subqueries that make SQL readable
WITH inpatient AS (
    SELECT * FROM encounters WHERE encounter_class = 'inpatient'
)
SELECT * FROM inpatient;
```

#### Window Functions
```sql
-- LEAD: look at the NEXT row in a group
SELECT
    patient_id,
    start_date,
    LEAD(start_date) OVER (
        PARTITION BY patient_id ORDER BY start_date
    ) AS next_admission
FROM encounters;
```

This is the most important SQL concept in the project. `PARTITION BY patient_id` means "do this separately for each patient." `ORDER BY start_date` means "sort by date within each patient." `LEAD(start_date)` means "get the start_date of the next row."

#### DATE_TRUNC
```sql
-- Round a date to the month (for monthly aggregations)
SELECT DATE_TRUNC('month', start_date)::DATE AS month
FROM encounters;
```

#### PERCENTILE_CONT
```sql
-- Calculate median (50th percentile)
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_cost)
FROM encounters;
```

---

## PostgreSQL Basics for This Repo

### What PostgreSQL is
PostgreSQL (often called "Postgres") is a database server. It stores data in tables and lets you query it with SQL. Unlike SQLite (which is a single file), Postgres runs as a background service on your computer.

### Key commands

```bash
# Start PostgreSQL (Homebrew on macOS)
brew services start postgresql@14

# Create a database
createdb carepulse

# Connect to it
psql carepulse

# Inside psql:
\dt          -- list tables
\d patients  -- describe a table
\q           -- quit
```

### How this project uses PostgreSQL
1. `sql/schema.sql` creates all the tables
2. `run_etl.py` loads data from CSVs into those tables
3. `src/db.py` provides a Python connection via SQLAlchemy
4. Analytics modules run SQL queries through that connection
5. Streamlit reads query results and renders charts

---

## Streamlit Basics for This Repo

### What Streamlit is
Streamlit is a Python library that turns a Python script into a web page. You write Python → Streamlit renders it in a browser.

### Key Streamlit functions

```python
import streamlit as st

# Title and text
st.title("My Dashboard")
st.markdown("Some **bold** text")

# Metrics (KPI cards)
st.metric("Total Patients", "1,000")

# Columns (side by side layout)
col1, col2 = st.columns(2)
col1.metric("Metric A", "123")
col2.metric("Metric B", "456")

# Charts (using Plotly)
import plotly.express as px
fig = px.bar(df, x="month", y="count")
st.plotly_chart(fig, use_container_width=True)

# Filters
selected = st.selectbox("Choose facility", facility_list)
selected_types = st.multiselect("Filter by type", types, default=types)

# Tables
st.dataframe(df)

# Tabs
tab1, tab2 = st.tabs(["Tab A", "Tab B"])
with tab1:
    st.write("Content A")
```

### Multi-page apps
Streamlit supports multiple pages automatically. Put files in `app/pages/` and they appear in the sidebar. File names determine the order (hence `1_Executive_Overview.py`, `2_Cohort_Explorer.py`, etc.).

### How to run
```bash
streamlit run app/Home.py
```

---

## Plotly Basics for This Repo

### What Plotly is
Plotly creates interactive charts that you can hover over, zoom, and filter. It's used inside Streamlit for all visualizations.

### Common chart types used

```python
import plotly.express as px

# Bar chart
fig = px.bar(df, x="category", y="count", color="group")

# Line chart
fig = px.line(df, x="date", y="value", markers=True)

# Pie chart
fig = px.pie(df, values="count", names="category")

# Area chart
fig = px.area(df, x="date", y="value", color="type")

# Horizontal bar
fig = px.bar(df, y="name", x="value", orientation="h")

# Histogram
fig = px.histogram(df, x="days", nbins=30)

# Customization
fig.update_layout(title="My Chart", xaxis_title="X", yaxis_title="Y")
fig.update_traces(line_color="#E53935")
```

### Gauge chart (used in Data Quality page)
```python
import plotly.graph_objects as go

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=85,
    title={"text": "Quality Score"},
    gauge={"axis": {"range": [0, 100]}},
))
```

---

## Testing Basics for This Repo

### What pytest does
pytest finds files named `test_*.py`, finds functions named `test_*`, and runs them. If an `assert` statement fails, the test fails.

### How to run tests
```bash
pytest tests/ -v
```

### How tests are structured
```python
def test_age_group_binning():
    """Test that age 25 maps to '18-29' group."""
    ages = pd.Series([25])
    groups = pd.cut(ages, bins=[0, 18, 30], labels=["0-17", "18-29"])
    assert list(groups) == ["18-29"]
```

### What we test in this project
1. **Transformation logic** — age group binning, LOS calculation
2. **Readmission logic** — correct flagging of 30-day readmissions
3. **Data quality logic** — completeness calculation, duplicate detection

---

## dbt Basics for This Repo

### What dbt does
dbt (Data Build Tool) manages SQL transformations as version-controlled models. Instead of writing ad-hoc SQL scripts, you write `.sql` files that dbt compiles, runs, and tests.

### Key concepts

| Concept | Meaning |
|---------|---------|
| **Model** | A `.sql` file in `models/`. Each model becomes a table or view. |
| **Source** | A raw table that dbt reads from (defined in `sources.yml`). |
| **Staging model** | A light transformation of a source (rename, add computed columns). |
| **Mart model** | A business-ready aggregation built from staging models. |
| **Test** | An assertion on your data (e.g., this column must be unique). |
| **Profile** | Database connection settings (in `~/.dbt/profiles.yml`). |

### Our dbt project structure
```
dbt_carepulse/
├── dbt_project.yml             ← Project settings
├── models/
│   ├── staging/
│   │   ├── sources.yml         ← Declares raw tables as sources
│   │   ├── schema.yml          ← Tests for staging models
│   │   ├── stg_patients.sql    ← Adds current_age, age_group, is_alive
│   │   ├── stg_encounters.sql  ← Adds los_days, encounter_month
│   │   └── stg_conditions.sql  ← Dedupes, adds is_chronic flag
│   └── marts/
│       ├── schema.yml          ← Tests for mart models
│       ├── mart_readmissions.sql         ← 30-day readmission flagging (LEAD)
│       ├── mart_utilization_monthly.sql  ← Monthly aggregates by facility
│       └── mart_facility_performance.sql ← Facility scorecard with NTILE rankings
```

### Key dbt commands
```bash
cd dbt_carepulse
dbt debug          # Test database connection
dbt run            # Build all models
dbt test           # Run all tests (27 tests)
dbt build          # Run + test in one command
dbt docs generate  # Generate documentation
```

### Why dbt matters for interviews
- Shows you understand **transformation management**, not just ad-hoc SQL
- Tests prove your data contracts are enforced
- It's the industry standard tool for analytics engineering
- Demonstrates staging → mart pattern used at every modern data team

---

## HEDIS Basics for This Repo

### What HEDIS is
HEDIS (Healthcare Effectiveness Data and Information Set) is a set of quality measures published by NCQA (National Committee for Quality Assurance). Health plans are graded on these measures.

### Measures in this project

| Measure | Full Name | What It Measures |
|---------|-----------|-----------------|
| **ACR** | Plan All-Cause Readmissions | % of adults 18-64 readmitted within 30 days (lower is better) |
| **FUH** | Follow-Up After Hospitalization for Mental Illness | % of MH discharges with outpatient follow-up within 7/30 days (higher is better) |

### Why HEDIS matters for Kaiser interviews
- Kaiser Permanente reports HEDIS measures to NCQA annually
- Showing you understand HEDIS demonstrates healthcare domain knowledge
- ACR directly relates to the readmission analysis in this project

---

## GitHub Actions CI Basics

### What CI does
Continuous Integration (CI) automatically runs tests every time you push code. Our `.github/workflows/ci.yml` spins up a PostgreSQL database, runs the ETL, executes pytest, and builds dbt models.

### Two CI jobs
1. **test** — Installs app dependencies, runs ETL, runs `pytest tests/ -v`
2. **dbt** — Installs dbt, runs ETL, runs `dbt build`

They run in parallel, each with their own PostgreSQL service container.

### Why CI matters
- Catches breaking changes before they reach production
- Proves your code works on a clean machine (not just your laptop)
- The green badge in README shows the project is well-maintained

---

## How the Files Connect

```
src/config.py          ← Central settings (DB credentials, constants)
    ↓
src/db.py              ← Database connection (used by everything)
    ↓
src/etl/generate_*.py  ← Creates fake data CSVs
src/etl/load_raw.py    ← Loads CSVs into Postgres
src/etl/clean.py       ← Cleans data in Postgres
src/etl/transform.py   ← Builds readmissions table
    ↓
run_etl.py             ← Runs all ETL steps in order
    ↓
src/analysis/          ← Query functions (return DataFrames)
  readmissions.py      ← Readmission rate queries
  utilization.py       ← Volume, LOS, cost queries
  cohorts.py           ← Age/condition breakdowns
  facilities.py        ← Facility comparisons
  hedis.py             ← HEDIS quality measure queries (ACR, FUH)
  risk_model.py        ← Logistic regression readmission risk model
    ↓
dbt_carepulse/         ← dbt project (transformation layer)
  models/staging/      ← stg_patients, stg_encounters, stg_conditions
  models/marts/        ← mart_readmissions, mart_utilization, mart_facility
    ↓
app/pages/             ← Dashboard pages (import from src/analysis/)
  1_Executive_Overview.py
  2_Cohort_Explorer.py
  3_Readmission_Analysis.py
  4_Utilization_Trends.py
  5_Facility_Drilldown.py
  6_Data_Quality.py
  7_Model_Explainability.py  ← ROC curve, feature importance, interactive scorer
  8_HEDIS_Measures.py        ← NCQA-aligned ACR and FUH measures
```

---

## How Data Flows from Raw Input to Dashboard

```
Step 1: Generate Data
  run_etl.py → src/etl/generate_synthetic_data.py
  → Creates CSV files in data/raw/ (patients.csv, encounters.csv, etc.)

Step 2: Load into Database
  run_etl.py → sql/schema.sql (creates empty tables)
  run_etl.py → src/etl/load_raw.py (reads CSVs with pandas → writes to Postgres)

Step 3: Clean
  run_etl.py → src/etl/clean.py
  → Removes duplicates, fixes bad dates, validates required fields

Step 4: Transform
  run_etl.py → src/etl/transform.py
  → Builds the readmissions table (window function logic in Python)

Step 5: Query
  app/pages/*.py → src/analysis/*.py → src/db.py → PostgreSQL
  → Each analytics function sends a SQL query, gets back a DataFrame

Step 6: Render
  app/pages/*.py → Plotly chart → st.plotly_chart()
  → Streamlit renders the DataFrame as an interactive chart in the browser
```

---

## 14-Day Study Plan

### Week 1: Understand the Foundation

| Day | What to Study | Time | What to Do |
|-----|--------------|------|-----------|
| **1** | Read README.md and docs/architecture.md | 1 hr | Understand what the project does and how pieces connect |
| **2** | Read src/config.py and src/db.py | 1 hr | Understand how Python talks to the database |
| **3** | Read src/etl/generate_synthetic_data.py | 1.5 hr | Trace how fake data is created |
| **4** | Read src/etl/load_raw.py and src/etl/clean.py | 1 hr | Understand the ETL pipeline |
| **5** | Read src/etl/transform.py | 1.5 hr | This is the most important file — understand the readmission logic |
| **6** | Read all SQL files in sql/ | 2 hr | Understand each query, especially readmission_flag.sql |
| **7** | Run the full pipeline end-to-end | 1 hr | `python run_etl.py` then `streamlit run app/Home.py` |

### Week 2: Go Deeper

| Day | What to Study | Time | What to Do |
|-----|--------------|------|-----------|
| **8** | Read src/analysis/readmissions.py + utilization.py | 1.5 hr | Understand each query function |
| **9** | Read src/analysis/cohorts.py + facilities.py | 1 hr | Understand cohort and facility queries |
| **10** | Read dbt_carepulse/models/ (staging + marts) | 1.5 hr | Understand dbt staging → mart transformation chain |
| **11** | Read app/pages/1_Executive_Overview.py | 1 hr | Understand how data → chart in Streamlit |
| **12** | Read app/pages/3_Readmission_Analysis.py | 1.5 hr | The core dashboard page |
| **13** | Read sql/hedis_acr.sql + src/analysis/hedis.py | 1 hr | Understand HEDIS quality measures |
| **14** | Read app/pages/7_Model_Explainability.py | 1 hr | Understand the risk model + interactive scorer |

### Week 3: Polish and Practice

| Day | What to Study | Time | What to Do |
|-----|--------------|------|-----------|
| **15** | Read app/pages/6_Data_Quality.py and src/data_quality/checks.py | 1 hr | Understand DQ scoring |
| **16** | Read .github/workflows/ci.yml | 0.5 hr | Understand the CI pipeline |
| **17** | Read docs/architecture.md (data lineage diagram) | 1 hr | Trace data flow from source to dashboard |
| **18** | Read docs/interview_guide.md | 2 hr | Practice explaining the project |
| **19** | Practice the 1-minute and 5-minute pitches out loud | 1 hr | Say it 3 times until it's natural |

---

## Mini Exercises

These use the actual project files:

### Exercise 1: Modify an Age Group
Open `src/config.py`. Change `AGE_BINS` to split the 18-29 group into 18-24 and 25-29. Re-run the ETL and see how the dashboard changes.

### Exercise 2: Add a New Metric
In `src/analysis/utilization.py`, write a new function `get_avg_cost_by_payer()` that returns the average encounter cost grouped by payer. Then display it on the Executive Overview page.

### Exercise 3: Write a New SQL Query
Create `sql/top_providers.sql` that returns the top 10 providers by encounter volume, including their specialty and average cost. Add comments explaining each part.

### Exercise 4: Add a Test
In `tests/test_transforms.py`, add a test that verifies a patient aged 72 is assigned to the "60-74" age group.

### Exercise 5: Add a Chart
In `app/pages/4_Utilization_Trends.py`, add a new chart that shows the top 5 most expensive encounter types using a horizontal bar chart.

### Exercise 6: Read the SQL
Open `sql/readmission_flag.sql`. Without running it, trace through the logic and write on paper what each CTE does. Then run it in psql to verify.

---

## File Reading Order

Start here and read in this order:

1. `README.md` — what the project does
2. `docs/architecture.md` — how pieces connect + data lineage diagram
3. `docs/data_model.md` — what tables exist and why
4. `src/config.py` — settings and constants
5. `src/db.py` — how Python talks to the database
6. `sql/schema.sql` — table definitions
7. `src/etl/generate_synthetic_data.py` — where data comes from
8. `src/etl/load_raw.py` — loading data
9. `src/etl/clean.py` — cleaning data
10. `src/etl/transform.py` — **most important** — readmission logic
11. `sql/readmission_flag.sql` — same logic in pure SQL
12. `dbt_carepulse/models/staging/` — dbt staging models (stg_patients, stg_encounters, stg_conditions)
13. `dbt_carepulse/models/marts/` — dbt mart models (readmissions, utilization, facility performance)
14. `src/analysis/readmissions.py` — readmission query functions
15. `src/analysis/hedis.py` — HEDIS quality measure functions
16. `src/analysis/risk_model.py` — logistic regression risk model
17. `app/pages/1_Executive_Overview.py` — how data becomes a dashboard
18. `app/pages/3_Readmission_Analysis.py` — the core analytics page
19. `app/pages/7_Model_Explainability.py` — ML model visualization + interactive scorer
20. `app/pages/8_HEDIS_Measures.py` — NCQA-aligned quality reporting
21. `.github/workflows/ci.yml` — CI/CD pipeline configuration
22. `docs/interview_guide.md` — how to talk about it all

---

## Common Beginner Mistakes and How to Avoid Them

### 1. Forgetting to activate the virtual environment
**Symptom:** `ModuleNotFoundError: No module named 'streamlit'`
**Fix:** Always run `source .venv/bin/activate` before doing anything.

### 2. PostgreSQL not running
**Symptom:** `connection refused` error
**Fix:** Run `brew services start postgresql@14`

### 3. Database doesn't exist
**Symptom:** `FATAL: database "carepulse" does not exist`
**Fix:** Run `createdb carepulse`

### 4. .env file missing
**Symptom:** Wrong DB credentials or connection errors
**Fix:** Copy `.env.example` to `.env` and edit credentials

### 5. Running Streamlit from the wrong directory
**Symptom:** Import errors
**Fix:** Always run from the project root: `streamlit run app/Home.py`

### 6. Editing SQL but not re-running ETL
**Symptom:** Dashboard shows old data
**Fix:** If you changed schema.sql or transform logic, re-run `python run_etl.py`

### 7. Confusing the Python readmission logic with the SQL version
Both exist and do the same thing. The Python version (in `transform.py`) builds the table. The SQL version (in `readmission_flag.sql`) is for demonstration/documentation.

### 8. Not understanding what shift(-1) does
`shift(-1)` moves data UP by one position within a group. For patient encounters sorted by date, it gives you the NEXT encounter's values. The last encounter gets NaN (no next one).

### 9. Thinking the model is "the point"
The model is a small, optional addition. The real value is the data modeling, SQL, ETL, and dashboard. Don't spend 80% of an interview on the model.

### 10. Memorizing without understanding
Don't memorize query outputs. Instead, understand the logic so you can answer "what if we changed the window to 60 days?" off the cuff. Interviewers can tell the difference.
