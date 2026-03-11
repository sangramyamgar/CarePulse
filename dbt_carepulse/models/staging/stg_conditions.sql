-- stg_conditions.sql
-- Staging model: deduplicated conditions with chronic flag.

SELECT DISTINCT
    patient_id,
    encounter_id,
    code            AS condition_code,
    description     AS condition_description,
    onset_date,
    resolved_date,
    CASE WHEN resolved_date IS NULL THEN TRUE ELSE FALSE END AS is_chronic
FROM {{ source('carepulse', 'conditions') }}
WHERE description IS NOT NULL
