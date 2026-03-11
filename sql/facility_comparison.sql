-- ============================================================================
-- Facility Comparison
--
-- Ranks facilities on key metrics to identify high-performing
-- and struggling sites.
-- ============================================================================

SELECT
    o.name                                                      AS facility_name,
    o.city,
    COUNT(e.id)                                                 AS total_encounters,
    COUNT(DISTINCT e.patient_id)                                AS unique_patients,
    ROUND(AVG(e.total_cost), 2)                                 AS avg_encounter_cost,
    -- Average length of stay for inpatient only
    ROUND(
        AVG(
            CASE WHEN e.encounter_class = 'inpatient'
                 THEN EXTRACT(DAY FROM (e.end_date - e.start_date))
            END
        ), 1
    ) AS avg_los_days,
    -- 30-day readmission rate (joins to readmissions table)
    ROUND(
        100.0 * SUM(CASE WHEN r.is_30day_readmit THEN 1 ELSE 0 END)
            / NULLIF(SUM(CASE WHEN e.encounter_class = 'inpatient' THEN 1 ELSE 0 END), 0),
        1
    ) AS readmit_rate_pct
FROM encounters e
JOIN organizations o ON e.org_id = o.id
LEFT JOIN readmissions r ON e.id = r.encounter_id
GROUP BY o.name, o.city
ORDER BY total_encounters DESC;
