-- hedis_fuh.sql
-- HEDIS FUH — Follow-Up After Hospitalization for Mental Illness (simplified)
--
-- Specification summary (adapted for synthetic data):
--   Denominator: Acute inpatient discharges with a principal diagnosis
--                of mental illness (mapped to our synthetic conditions).
--   Numerator:   Patients with an outpatient/ambulatory follow-up visit
--                within 7 days (FUH-7) or 30 days (FUH-30) of discharge.
--   Exclusions:  Patients who died, transferred, or left AMA.
--
-- Since our synthetic data uses SNOMED-like descriptions, we map
-- "mental illness" to conditions containing relevant keywords.
--
-- Reference: NCQA HEDIS MY 2024 — Follow-Up After Hospitalization
--            for Mental Illness (FUH)

WITH mh_encounters AS (
    SELECT DISTINCT
        e.id              AS encounter_id,
        e.patient_id,
        e.end_date        AS discharge_date,
        e.org_id,
        e.payer
    FROM encounters e
    JOIN conditions c ON e.id = c.encounter_id
    WHERE e.encounter_class = 'inpatient'
      AND e.end_date IS NOT NULL
      AND (
          LOWER(c.description) LIKE '%depressive%'
          OR LOWER(c.description) LIKE '%anxiety%'
          OR LOWER(c.description) LIKE '%bipolar%'
          OR LOWER(c.description) LIKE '%schizophreni%'
          OR LOWER(c.description) LIKE '%psycho%'
          OR LOWER(c.description) LIKE '%mental%'
          OR LOWER(c.description) LIKE '%stress%disorder%'
      )
),

followups AS (
    SELECT
        mh.encounter_id,
        mh.patient_id,
        mh.discharge_date,
        mh.org_id,
        mh.payer,
        MIN(
            CASE WHEN fu.encounter_class IN ('outpatient', 'ambulatory')
                  AND fu.start_date > mh.discharge_date
                  AND fu.start_date <= mh.discharge_date + INTERVAL '7 days'
            THEN fu.start_date END
        ) AS followup_7d,
        MIN(
            CASE WHEN fu.encounter_class IN ('outpatient', 'ambulatory')
                  AND fu.start_date > mh.discharge_date
                  AND fu.start_date <= mh.discharge_date + INTERVAL '30 days'
            THEN fu.start_date END
        ) AS followup_30d
    FROM mh_encounters mh
    LEFT JOIN encounters fu ON mh.patient_id = fu.patient_id
    GROUP BY mh.encounter_id, mh.patient_id, mh.discharge_date, mh.org_id, mh.payer
)

SELECT
    COUNT(*)                                    AS denominator,
    SUM(CASE WHEN followup_7d IS NOT NULL
         THEN 1 ELSE 0 END)                    AS numerator_7d,
    ROUND(100.0 * SUM(CASE WHEN followup_7d IS NOT NULL
         THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS fuh_7d_rate_pct,
    SUM(CASE WHEN followup_30d IS NOT NULL
         THEN 1 ELSE 0 END)                    AS numerator_30d,
    ROUND(100.0 * SUM(CASE WHEN followup_30d IS NOT NULL
         THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS fuh_30d_rate_pct
FROM followups
