# CarePulse: Readmission & Utilization Analytics Platform

[![CI — Tests & Data Contracts](https://github.com/sangramyamgar/CarePulse/actions/workflows/ci.yml/badge.svg)](https://github.com/sangramyamgar/CarePulse/actions/workflows/ci.yml)

A healthcare analytics project that ingests synthetic patient data, models it in PostgreSQL, computes readmission rates and utilization metrics, and surfaces insights through an interactive Streamlit dashboard.

## What This Project Does

CarePulse answers the questions hospital leadership actually asks:

- **Which patient groups keep coming back within 30 days?**
- **How does utilization vary across facilities, age groups, and conditions?**
- **Where are our operational hotspots?**
- **Is our data complete and trustworthy?**

## Architecture

```
Synthea CSVs → Python ETL → PostgreSQL → SQL Analytics → Streamlit Dashboard
```

See [docs/architecture.md](docs/architecture.md) for the full diagram.

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- macOS (tested) or Linux

### Setup

```bash
# 1. Clone and enter the project
cd Kaiser

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy and edit environment config
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# 5. Create the database
createdb carepulse

# 6. Generate synthetic data (creates CSVs in data/raw/)
python src/etl/generate_synthetic_data.py

# 7. Run the full ETL pipeline
python run_etl.py

# 8. Launch the dashboard
streamlit run app/Home.py
```

## Project Structure

```
Kaiser/
├── app/                  # Streamlit dashboard (multi-page)
├── src/
│   ├── etl/              # Extract, transform, load
│   ├── analysis/         # Analytics logic (readmissions, utilization, cohorts)
│   ├── features/         # Derived tables and risk flags
│   └── data_quality/     # Data completeness and validity checks
├── sql/                  # Standalone SQL queries (well-commented)
├── tests/                # pytest test suite
├── notebooks/            # Exploration only (not the product)
├── data/raw/             # Synthea-style CSVs
├── data/processed/       # Intermediate outputs
└── docs/                 # Architecture, data model, interview guides
```

## Key Metrics

| Metric | Definition |
|---|---|
| 30-Day Readmission Rate | % of inpatient discharges with a re-admission within 30 days |
| Avg Length of Stay (ALOS) | Mean inpatient encounter duration in days |
| ED Utilization Rate | Emergency visits per 1,000 patients per month |
| Chronic Condition Prevalence | % of patients with multiple chronic conditions |

## Tech Stack

- **Python** — data processing, ETL, dashboard
- **pandas** — data manipulation
- **PostgreSQL** — relational data storage
- **SQLAlchemy** — database access layer
- **Streamlit** — interactive dashboard
- **Plotly** — charts and visualizations
- **pytest** — testing

## Documentation

- [Project Plan](docs/project_plan.md)
- [Architecture](docs/architecture.md)
- [Data Model](docs/data_model.md)
- [Interview Guide](docs/interview_guide.md)
- [Learning Guide](docs/learn_the_tech_stack_from_basics.md)
- [Mac + VS Code Setup](docs/mac_vscode_setup_guide.md)

## License

This project uses synthetic data only. No real patient data is included or required.
