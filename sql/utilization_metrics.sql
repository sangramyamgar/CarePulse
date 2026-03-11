-- ============================================================================
-- Utilization Metrics
--
-- Computes key utilization summaries:
--   • Encounter volume by type and month
--   • Average length of stay (ALOS) for inpatient encounters
--   • Total and average cost by encounter class
-- ============================================================================

-- ----- Monthly encounter volume by class -----
SELECT
    DATE_TRUNC('month', e.start_date)::DATE AS month,
    e.encounter_class,
    COUNT(*)                                AS encounter_count,
    COUNT(DISTINCT e.patient_id)            AS unique_patients,
    ROUND(AVG(e.total_cost), 2)             AS avg_cost,
    ROUND(SUM(e.total_cost), 2)             AS total_cost
FROM encounters e
GROUP BY 1, 2
ORDER BY 1, 2;
