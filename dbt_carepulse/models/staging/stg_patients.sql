-- stg_patients.sql
-- Staging model: clean patient demographics from the raw patients table.

SELECT
    id              AS patient_id,
    birth_date,
    death_date,
    gender,
    race,
    ethnicity,
    city,
    state,
    zip,
    county,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date))::INTEGER AS current_age,
    CASE
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date))::INTEGER < 18 THEN '0-17'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date))::INTEGER < 30 THEN '18-29'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date))::INTEGER < 45 THEN '30-44'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date))::INTEGER < 60 THEN '45-59'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date))::INTEGER < 75 THEN '60-74'
        ELSE '75+'
    END AS age_group,
    CASE WHEN death_date IS NULL THEN TRUE ELSE FALSE END AS is_alive
FROM {{ source('carepulse', 'patients') }}
