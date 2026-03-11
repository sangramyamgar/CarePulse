-- mart_readmissions.sql
-- Core readmission analytics table.
-- For each inpatient encounter, calculate days to next admission
-- and flag 30-day readmissions.

WITH inpatient AS (
    SELECT
        e.encounter_id,
        e.patient_id,
        e.org_id,
        e.payer,
        e.encounter_class,
        e.end_date      AS discharge_date,
        e.los_days,
        e.total_cost,
        p.current_age   AS age_at_encounter,
        p.age_group,
        EXTRACT(YEAR FROM AGE(e.start_date, p.birth_date))::INTEGER AS age_at_visit
    FROM {{ ref('stg_encounters') }} e
    JOIN {{ ref('stg_patients') }} p ON e.patient_id = p.patient_id
    WHERE e.encounter_class = 'inpatient'
      AND e.end_date IS NOT NULL
),

-- Get primary condition per encounter (first listed)
primary_conditions AS (
    SELECT DISTINCT ON (encounter_id)
        encounter_id,
        condition_description AS primary_condition
    FROM {{ ref('stg_conditions') }}
    ORDER BY encounter_id, onset_date
),

-- Count chronic conditions per patient
chronic_counts AS (
    SELECT
        patient_id,
        COUNT(DISTINCT condition_code) AS chronic_count
    FROM {{ ref('stg_conditions') }}
    WHERE is_chronic = TRUE
    GROUP BY patient_id
),

-- Use LEAD to find the next admission date for the same patient
with_next AS (
    SELECT
        i.*,
        pc.primary_condition,
        COALESCE(cc.chronic_count, 0) AS chronic_count,
        LEAD(i.discharge_date) OVER (
            PARTITION BY i.patient_id
            ORDER BY i.discharge_date
        ) AS next_admit_date
    FROM inpatient i
    LEFT JOIN primary_conditions pc ON i.encounter_id = pc.encounter_id
    LEFT JOIN chronic_counts cc ON i.patient_id = cc.patient_id
)

SELECT
    encounter_id,
    patient_id,
    discharge_date,
    next_admit_date,
    EXTRACT(DAY FROM (next_admit_date - discharge_date))::INTEGER AS days_to_readmit,
    CASE
        WHEN next_admit_date IS NOT NULL
         AND EXTRACT(DAY FROM (next_admit_date - discharge_date))::INTEGER <= 30
        THEN TRUE
        ELSE FALSE
    END AS is_30day_readmit,
    age_at_encounter,
    age_group,
    primary_condition,
    chronic_count,
    encounter_class,
    payer,
    org_id

FROM with_next
