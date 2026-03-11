-- mart_utilization_monthly.sql
-- Monthly encounter volume broken down by facility and service line.

SELECT
    e.encounter_month                           AS month,
    o.name                                      AS facility_name,
    e.encounter_class,
    COUNT(*)                                    AS encounter_count,
    COUNT(DISTINCT e.patient_id)                AS unique_patients,
    ROUND(AVG(e.total_cost), 2)                 AS avg_cost,
    ROUND(SUM(e.total_cost), 2)                 AS total_cost,
    ROUND(AVG(e.los_days), 1)                   AS avg_los_days

FROM {{ ref('stg_encounters') }} e
LEFT JOIN {{ source('carepulse', 'organizations') }} o ON e.org_id = o.id

GROUP BY 1, 2, 3
ORDER BY 1, 2, 3
