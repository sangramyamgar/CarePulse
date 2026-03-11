-- mart_facility_performance.sql
-- Facility-level scorecard with key operational metrics.

WITH encounter_stats AS (
    SELECT
        e.org_id,
        COUNT(*)                                AS total_encounters,
        COUNT(DISTINCT e.patient_id)            AS unique_patients,
        ROUND(AVG(e.total_cost), 2)             AS avg_encounter_cost,
        ROUND(AVG(
            CASE WHEN e.encounter_class = 'inpatient' THEN e.los_days END
        ), 1)                                   AS avg_los_days
    FROM {{ ref('stg_encounters') }} e
    GROUP BY e.org_id
),

readmit_stats AS (
    SELECT
        org_id,
        COUNT(*)                                AS inpatient_count,
        SUM(CASE WHEN is_30day_readmit THEN 1 ELSE 0 END) AS readmissions,
        ROUND(
            100.0 * SUM(CASE WHEN is_30day_readmit THEN 1 ELSE 0 END)
            / NULLIF(COUNT(*), 0), 1
        )                                       AS readmit_rate_pct,
        -- Quartile ranking across facilities
        NTILE(4) OVER (
            ORDER BY 100.0 * SUM(CASE WHEN is_30day_readmit THEN 1 ELSE 0 END)
                     / NULLIF(COUNT(*), 0)
        )                                       AS readmit_quartile
    FROM {{ ref('mart_readmissions') }}
    GROUP BY org_id
)

SELECT
    o.name                      AS facility_name,
    o.city,
    o.state,
    es.total_encounters,
    es.unique_patients,
    es.avg_encounter_cost,
    es.avg_los_days,
    COALESCE(rs.readmit_rate_pct, 0)    AS readmit_rate_pct,
    COALESCE(rs.readmit_quartile, 1)    AS readmit_quartile,
    -- Percentile rank for ALOS
    NTILE(4) OVER (ORDER BY es.avg_los_days)       AS los_quartile,
    -- Percentile rank for cost
    NTILE(4) OVER (ORDER BY es.avg_encounter_cost)  AS cost_quartile

FROM {{ source('carepulse', 'organizations') }} o
LEFT JOIN encounter_stats es ON o.id = es.org_id
LEFT JOIN readmit_stats rs ON o.id = rs.org_id

ORDER BY es.total_encounters DESC
