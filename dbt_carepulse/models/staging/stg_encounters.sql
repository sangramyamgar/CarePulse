-- stg_encounters.sql
-- Staging model: cleaned encounters with derived fields.

SELECT
    id              AS encounter_id,
    patient_id,
    provider_id,
    org_id,
    payer,
    encounter_class,
    start_date,
    end_date,
    total_cost,
    reason_description,
    EXTRACT(DAY FROM (end_date - start_date))::INTEGER AS los_days,
    DATE_TRUNC('month', start_date)::DATE AS encounter_month,
    EXTRACT(MONTH FROM start_date)::INTEGER AS month_num,
    EXTRACT(YEAR FROM start_date)::INTEGER AS year_num
FROM {{ source('carepulse', 'encounters') }}
WHERE start_date IS NOT NULL
