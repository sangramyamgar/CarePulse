-- ============================================================================
-- 30-Day Readmission Flag
-- 
-- Logic: For each inpatient encounter, find the next inpatient admission
-- for the same patient using a window function. If the gap between
-- discharge and next admission is ≤ 30 days, flag as a readmission.
-- ============================================================================

WITH inpatient_encounters AS (
    -- Step 1: Filter to inpatient encounters only
    SELECT
        e.id AS encounter_id,
        e.patient_id,
        e.end_date AS discharge_date,
        e.start_date,
        e.encounter_class,
        e.payer,
        e.org_id
    FROM encounters e
    WHERE e.encounter_class = 'inpatient'
      AND e.end_date IS NOT NULL
),

with_next_admit AS (
    -- Step 2: Use LEAD() window function to find next admission date per patient
    SELECT
        ie.*,
        LEAD(ie.start_date) OVER (
            PARTITION BY ie.patient_id
            ORDER BY ie.start_date
        ) AS next_admit_date
    FROM inpatient_encounters ie
)

-- Step 3: Calculate days between discharge and next admission
SELECT
    wna.encounter_id,
    wna.patient_id,
    wna.discharge_date,
    wna.next_admit_date,
    EXTRACT(DAY FROM (wna.next_admit_date - wna.discharge_date))::INTEGER AS days_to_readmit,
    CASE
        WHEN wna.next_admit_date IS NOT NULL
         AND EXTRACT(DAY FROM (wna.next_admit_date - wna.discharge_date)) <= 30
        THEN TRUE
        ELSE FALSE
    END AS is_30day_readmit,
    wna.encounter_class,
    wna.payer,
    wna.org_id
FROM with_next_admit wna
ORDER BY wna.patient_id, wna.start_date;
