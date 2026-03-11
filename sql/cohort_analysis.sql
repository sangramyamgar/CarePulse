-- ============================================================================
-- Cohort Analysis
--
-- Breaks down readmission rates by patient cohort dimensions:
--   • Age group
--   • Primary condition
--   • Payer
-- ============================================================================

-- ----- Readmission rate by age group -----
SELECT
    r.age_group,
    COUNT(*)                                                    AS total_encounters,
    SUM(CASE WHEN r.is_30day_readmit THEN 1 ELSE 0 END)       AS readmissions,
    ROUND(
        100.0 * SUM(CASE WHEN r.is_30day_readmit THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0),
        1
    ) AS readmission_rate_pct
FROM readmissions r
GROUP BY r.age_group
ORDER BY r.age_group;
