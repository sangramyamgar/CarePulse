-- hedis_acr.sql
-- HEDIS ACR — All-Cause Readmissions (simplified from NCQA specs)
--
-- Specification summary (simplified for synthetic data):
--   Denominator: Acute inpatient discharges for patients 18-64
--                during the measurement year.
--   Numerator:   Unplanned acute readmissions within 30 days of
--                an index discharge.
--   Exclusions:  Planned readmissions (not modeled in this synthetic set),
--                patients who died during the index stay.
--
-- Reference: NCQA HEDIS MY 2024 — Plan All-Cause Readmissions (PCR)

WITH index_stays AS (
    SELECT
        e.id                  AS encounter_id,
        e.patient_id,
        e.end_date            AS discharge_date,
        e.org_id,
        e.payer,
        EXTRACT(YEAR FROM AGE(e.start_date, p.birth_date))::INTEGER AS age_at_admit
    FROM encounters e
    JOIN patients p ON e.patient_id = p.id
    WHERE e.encounter_class = 'inpatient'
      AND e.end_date IS NOT NULL
      -- ACR targets adults 18-64 (commercial / Medicaid)
      AND EXTRACT(YEAR FROM AGE(e.start_date, p.birth_date))::INTEGER BETWEEN 18 AND 64
      -- Exclude deaths during stay
      AND (p.death_date IS NULL OR p.death_date > e.end_date)
),

with_readmit AS (
    SELECT
        i.*,
        LEAD(i.discharge_date) OVER (
            PARTITION BY i.patient_id ORDER BY i.discharge_date
        ) AS next_admit_date,
        EXTRACT(DAY FROM (
            LEAD(i.discharge_date) OVER (
                PARTITION BY i.patient_id ORDER BY i.discharge_date
            ) - i.discharge_date
        ))::INTEGER AS days_to_readmit
    FROM index_stays i
)

SELECT
    COUNT(*) AS denominator,
    SUM(CASE WHEN days_to_readmit IS NOT NULL
              AND days_to_readmit <= 30 THEN 1 ELSE 0 END) AS numerator,
    ROUND(
        100.0 * SUM(CASE WHEN days_to_readmit IS NOT NULL
                          AND days_to_readmit <= 30 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0), 2
    ) AS acr_rate_pct
FROM with_readmit
