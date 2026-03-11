-- ============================================================================
-- CarePulse: Database Schema
-- Creates all tables for the healthcare analytics platform.
-- Run this file against your PostgreSQL database before loading data.
-- ============================================================================

-- Drop tables in reverse dependency order (for re-runs)
DROP TABLE IF EXISTS readmissions CASCADE;
DROP TABLE IF EXISTS medications CASCADE;
DROP TABLE IF EXISTS procedures CASCADE;
DROP TABLE IF EXISTS conditions CASCADE;
DROP TABLE IF EXISTS encounters CASCADE;
DROP TABLE IF EXISTS providers CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;
DROP TABLE IF EXISTS patients CASCADE;

-- ---------------------------------------------------------------------------
-- Organizations (hospitals / facilities)
-- ---------------------------------------------------------------------------
CREATE TABLE organizations (
    id          VARCHAR(36) PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    city        VARCHAR(100),
    state       VARCHAR(2),
    zip         VARCHAR(10)
);

-- ---------------------------------------------------------------------------
-- Providers (doctors / clinicians)
-- ---------------------------------------------------------------------------
CREATE TABLE providers (
    id          VARCHAR(36) PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    specialty   VARCHAR(100),
    org_id      VARCHAR(36) REFERENCES organizations(id)
);

-- ---------------------------------------------------------------------------
-- Patients
-- ---------------------------------------------------------------------------
CREATE TABLE patients (
    id          VARCHAR(36) PRIMARY KEY,
    birth_date  DATE NOT NULL,
    death_date  DATE,
    gender      VARCHAR(1) NOT NULL,
    race        VARCHAR(50),
    ethnicity   VARCHAR(50),
    city        VARCHAR(100),
    state       VARCHAR(2),
    zip         VARCHAR(10),
    county      VARCHAR(100)
);

-- ---------------------------------------------------------------------------
-- Encounters (visits / admissions)
-- ---------------------------------------------------------------------------
CREATE TABLE encounters (
    id                  VARCHAR(36) PRIMARY KEY,
    patient_id          VARCHAR(36) NOT NULL REFERENCES patients(id),
    provider_id         VARCHAR(36) REFERENCES providers(id),
    org_id              VARCHAR(36) REFERENCES organizations(id),
    payer               VARCHAR(100),
    encounter_class     VARCHAR(20) NOT NULL,
    start_date          TIMESTAMP NOT NULL,
    end_date            TIMESTAMP,
    total_cost          NUMERIC(12,2),
    reason_description  TEXT
);

-- Index on patient + date for readmission window queries
CREATE INDEX idx_encounters_patient_date ON encounters(patient_id, start_date);
CREATE INDEX idx_encounters_class ON encounters(encounter_class);

-- ---------------------------------------------------------------------------
-- Conditions (diagnoses attached to encounters)
-- ---------------------------------------------------------------------------
CREATE TABLE conditions (
    patient_id      VARCHAR(36) NOT NULL REFERENCES patients(id),
    encounter_id    VARCHAR(36) NOT NULL REFERENCES encounters(id),
    code            VARCHAR(20),
    description     TEXT,
    onset_date      DATE,
    resolved_date   DATE
);

CREATE INDEX idx_conditions_patient ON conditions(patient_id);
CREATE INDEX idx_conditions_encounter ON conditions(encounter_id);

-- ---------------------------------------------------------------------------
-- Procedures
-- ---------------------------------------------------------------------------
CREATE TABLE procedures (
    patient_id      VARCHAR(36) NOT NULL REFERENCES patients(id),
    encounter_id    VARCHAR(36) NOT NULL REFERENCES encounters(id),
    code            VARCHAR(20),
    description     TEXT,
    date            DATE,
    cost            NUMERIC(12,2)
);

-- ---------------------------------------------------------------------------
-- Medications
-- ---------------------------------------------------------------------------
CREATE TABLE medications (
    patient_id      VARCHAR(36) NOT NULL REFERENCES patients(id),
    encounter_id    VARCHAR(36) NOT NULL REFERENCES encounters(id),
    code            VARCHAR(20),
    description     TEXT,
    start_date      DATE,
    stop_date       DATE,
    cost            NUMERIC(12,2)
);

-- ---------------------------------------------------------------------------
-- Readmissions (derived / analytic table — populated by ETL)
-- ---------------------------------------------------------------------------
CREATE TABLE readmissions (
    encounter_id        VARCHAR(36) REFERENCES encounters(id),
    patient_id          VARCHAR(36) REFERENCES patients(id),
    discharge_date      TIMESTAMP,
    next_admit_date     TIMESTAMP,
    days_to_readmit     INTEGER,
    is_30day_readmit    BOOLEAN,
    age_at_encounter    INTEGER,
    age_group           VARCHAR(10),
    primary_condition   TEXT,
    chronic_count       INTEGER,
    encounter_class     VARCHAR(20),
    payer               VARCHAR(100),
    org_id              VARCHAR(36)
);

CREATE INDEX idx_readmissions_patient ON readmissions(patient_id);
CREATE INDEX idx_readmissions_30day ON readmissions(is_30day_readmit);
