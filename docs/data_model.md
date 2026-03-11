# CarePulse — Data Model

## Overview

The data model follows a **Synthea-style** healthcare schema: a central `patients` table linked to `encounters`, which in turn connect to `conditions`, `procedures`, and `medications`. Provider and facility data live in `providers` and `organizations`.

A derived `readmissions` table is built by the ETL pipeline to power readmission analytics.

## Entity-Relationship Diagram

```
patients ──< encounters >── providers
                │                │
                │                └── organizations
                │
        ┌───────┼───────┐
        ▼       ▼       ▼
   conditions procedures medications
```

One patient has many encounters. Each encounter can have many conditions, procedures, and medications.

## Table Definitions

### patients
| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR(36) PK | Unique patient identifier |
| birth_date | DATE | Date of birth |
| death_date | DATE | Date of death (NULL if alive) |
| gender | VARCHAR(1) | M or F |
| race | VARCHAR(50) | Race category |
| ethnicity | VARCHAR(50) | Ethnicity |
| city | VARCHAR(100) | City of residence |
| state | VARCHAR(2) | State abbreviation |
| zip | VARCHAR(10) | ZIP code |
| county | VARCHAR(100) | County |

### encounters
| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR(36) PK | Unique encounter identifier |
| patient_id | VARCHAR(36) FK | → patients.id |
| provider_id | VARCHAR(36) FK | → providers.id |
| org_id | VARCHAR(36) FK | → organizations.id |
| payer | VARCHAR(100) | Insurance payer name |
| encounter_class | VARCHAR(20) | inpatient, outpatient, emergency, etc. |
| start_date | TIMESTAMP | Encounter start |
| end_date | TIMESTAMP | Encounter end |
| total_cost | NUMERIC(12,2) | Total encounter cost |
| reason_description | TEXT | Primary reason for visit |

### conditions
| Column | Type | Description |
|--------|------|-------------|
| patient_id | VARCHAR(36) FK | → patients.id |
| encounter_id | VARCHAR(36) FK | → encounters.id |
| code | VARCHAR(20) | SNOMED code |
| description | TEXT | Condition name |
| onset_date | DATE | When the condition started |
| resolved_date | DATE | When resolved (NULL if ongoing) |

### procedures
| Column | Type | Description |
|--------|------|-------------|
| patient_id | VARCHAR(36) FK | → patients.id |
| encounter_id | VARCHAR(36) FK | → encounters.id |
| code | VARCHAR(20) | SNOMED code |
| description | TEXT | Procedure name |
| date | DATE | When performed |
| cost | NUMERIC(12,2) | Procedure cost |

### medications
| Column | Type | Description |
|--------|------|-------------|
| patient_id | VARCHAR(36) FK | → patients.id |
| encounter_id | VARCHAR(36) FK | → encounters.id |
| code | VARCHAR(20) | RxNorm code |
| description | TEXT | Medication name |
| start_date | DATE | Start of medication |
| stop_date | DATE | End of medication (NULL if ongoing) |
| cost | NUMERIC(12,2) | Medication cost |

### providers
| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR(36) PK | Unique provider identifier |
| name | VARCHAR(200) | Provider name |
| specialty | VARCHAR(100) | Medical specialty |
| org_id | VARCHAR(36) FK | → organizations.id |

### organizations
| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR(36) PK | Unique organization identifier |
| name | VARCHAR(200) | Facility/hospital name |
| city | VARCHAR(100) | City |
| state | VARCHAR(2) | State |
| zip | VARCHAR(10) | ZIP code |

### readmissions (derived)
| Column | Type | Description |
|--------|------|-------------|
| encounter_id | VARCHAR(36) FK | The index (initial) encounter |
| patient_id | VARCHAR(36) FK | Patient |
| discharge_date | TIMESTAMP | End of the index encounter |
| next_admit_date | TIMESTAMP | Start of the next inpatient encounter |
| days_to_readmit | INTEGER | Calendar days between discharge and next admit |
| is_30day_readmit | BOOLEAN | TRUE if days_to_readmit ≤ 30 |
| age_at_encounter | INTEGER | Patient age at the index encounter |
| age_group | VARCHAR(10) | Derived from age bins |
| primary_condition | TEXT | Most relevant condition for the encounter |
| chronic_count | INTEGER | Number of active chronic conditions |
| encounter_class | VARCHAR(20) | Class of the index encounter |
| payer | VARCHAR(100) | Payer for the index encounter |
| org_id | VARCHAR(36) | Facility of the index encounter |

## Key Relationships

- Every `encounter` belongs to exactly one `patient`, one `provider`, and one `organization`
- `conditions`, `procedures`, and `medications` link to both `patient` and `encounter`
- The `readmissions` table is a **derived/analytic table** built by joining encounters with a self-join using a window function to find the next admission per patient
