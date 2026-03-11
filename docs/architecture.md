# CarePulse — Architecture

## Overview

CarePulse follows a simple **ETL → Analytics → Dashboard** architecture that mirrors real healthcare data warehousing, scaled down for a portfolio project.

## Data Flow

```
┌─────────────────┐
│ Synthetic Data   │  Python script generates realistic CSV files
│ Generator        │  (Synthea-style: patients, encounters, conditions, etc.)
└────────┬────────┘
         │  CSVs
         ▼
┌─────────────────┐
│ ETL Pipeline     │  Python + pandas
│ (src/etl/)       │  • Load CSVs
│                  │  • Clean: dedup, parse dates, handle nulls
│                  │  • Validate: type checks, range checks
│                  │  • Write to PostgreSQL via SQLAlchemy
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ PostgreSQL       │  Normalized relational tables
│ (local)          │  • patients, encounters, conditions
│                  │  • procedures, medications
│                  │  • providers, organizations
│                  │  • readmissions (derived)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Analytics Layer  │  SQL files (sql/) + Python (src/analysis/)
│                  │  • Readmission logic with CTEs & window functions
│                  │  • Utilization aggregations
│                  │  • Cohort breakdowns
│                  │  • Data quality queries
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Streamlit App    │  Multi-page dashboard (app/)
│                  │  • Executive Overview with KPI cards
│                  │  • Cohort Explorer with filters
│                  │  • Readmission deep-dive
│                  │  • Utilization trends (Plotly)
│                  │  • Facility/Provider drilldown
│                  │  • Data Quality monitor
└─────────────────┘
```

## Why This Architecture

| Decision | Reason |
|----------|--------|
| Separate ETL scripts | Reproducible pipeline; easy to re-run |
| SQL in `.sql` files | SQL skills visible; reusable outside Python |
| Python analytics wrappers | Bridge between SQL results and dashboard |
| Streamlit multi-page | Each page = one analytic focus area |
| No orchestrator (Airflow) | Overkill for a local project; would obscure the analytics |

## Component Interaction

1. `run_etl.py` calls `src/etl/` modules in order: generate → load → clean → transform
2. `sql/schema.sql` defines all table structures
3. `src/analysis/` modules call `src/db.py` which reads SQL files and returns DataFrames
4. `app/` pages import from `src/analysis/` and render with Plotly

## Database

- **Engine**: PostgreSQL 14+ (local via Homebrew)
- **ORM**: None — we use raw SQL via SQLAlchemy's `text()` for transparency
- **Connection**: Single `engine` object in `src/db.py`

## Data Lineage

The diagram below traces every table from raw source through transformation to the dashboard page that consumes it.

```mermaid
flowchart LR
    subgraph Sources["Raw CSV Sources"]
        CSV_P[patients.csv]
        CSV_E[encounters.csv]
        CSV_C[conditions.csv]
        CSV_PR[procedures.csv]
        CSV_M[medications.csv]
        CSV_O[organizations.csv]
        CSV_PV[providers.csv]
    end

    subgraph ETL["ETL Pipeline  (src/etl/)"]
        LOAD[load_csv]
        CLEAN[clean & validate]
    end

    subgraph PG["PostgreSQL Tables"]
        T_PAT[patients]
        T_ENC[encounters]
        T_COND[conditions]
        T_PROC[procedures]
        T_MED[medications]
        T_ORG[organizations]
        T_PROV[providers]
        T_READ[readmissions]
    end

    subgraph DBT["dbt Models  (dbt_carepulse/)"]
        STG_P[stg_patients]
        STG_E[stg_encounters]
        STG_C[stg_conditions]
        MART_R[mart_readmissions]
        MART_U[mart_utilization_monthly]
        MART_F[mart_facility_performance]
    end

    subgraph HEDIS_SQL["HEDIS Measure SQL"]
        ACR[hedis_acr.sql]
        FUH[hedis_fuh.sql]
    end

    subgraph Analytics["Python Analytics  (src/analysis/)"]
        A_UTIL[utilization.py]
        A_READ[readmissions.py]
        A_COH[cohorts.py]
        A_FAC[facilities.py]
        A_DQ[data_quality]
        A_RISK[risk_model.py]
        A_HEDIS[hedis.py]
    end

    subgraph Dashboard["Streamlit Pages  (app/pages/)"]
        P1[1 Executive Overview]
        P2[2 Cohort Explorer]
        P3[3 Readmission Analysis]
        P4[4 Utilization Trends]
        P5[5 Facility Drilldown]
        P6[6 Data Quality]
        P7[7 Model Explainability]
        P8[8 HEDIS Measures]
    end

    CSV_P & CSV_E & CSV_C & CSV_PR & CSV_M & CSV_O & CSV_PV --> LOAD --> CLEAN

    CLEAN --> T_PAT & T_ENC & T_COND & T_PROC & T_MED & T_ORG & T_PROV
    T_ENC & T_COND & T_PAT --> T_READ

    T_PAT --> STG_P
    T_ENC --> STG_E
    T_COND --> STG_C
    STG_E & STG_C --> MART_R
    STG_E --> MART_U
    STG_E & MART_R --> MART_F

    T_ENC & T_PAT --> ACR
    T_ENC & T_COND --> FUH

    T_ENC & T_PAT & T_READ --> A_UTIL --> P1 & P4
    T_READ & T_COND --> A_READ --> P1 & P3
    T_PAT & T_COND --> A_COH --> P2
    T_ORG & T_ENC --> A_FAC --> P5
    T_PAT & T_ENC --> A_DQ --> P6
    T_READ --> A_RISK --> P7
    ACR & FUH --> A_HEDIS --> P8
```

### Reading the Diagram

| Layer | Description |
|-------|-------------|
| **Sources** | Synthea-generated CSVs dropped into `data/raw/` |
| **ETL** | `src/etl/` scripts load, clean, validate, and write to PostgreSQL |
| **PostgreSQL** | Normalized tables; `readmissions` is a derived table built during ETL |
| **dbt** | Staging models add computed columns; marts aggregate for BI queries |
| **HEDIS SQL** | Standalone measure definitions following NCQA specs |
| **Analytics** | Python modules wrap SQL queries and return DataFrames |
| **Dashboard** | Each Streamlit page imports one or more analytics modules |
