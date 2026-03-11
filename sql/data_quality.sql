-- ============================================================================
-- Data Quality Checks
--
-- Queries that surface data completeness and validity issues.
-- Used by the Data Quality Monitor dashboard page.
-- ============================================================================

-- ----- Table row counts -----
SELECT 'patients'       AS table_name, COUNT(*) AS row_count FROM patients
UNION ALL
SELECT 'encounters',     COUNT(*) FROM encounters
UNION ALL
SELECT 'conditions',     COUNT(*) FROM conditions
UNION ALL
SELECT 'procedures',     COUNT(*) FROM procedures
UNION ALL
SELECT 'medications',    COUNT(*) FROM medications
UNION ALL
SELECT 'providers',      COUNT(*) FROM providers
UNION ALL
SELECT 'organizations',  COUNT(*) FROM organizations
UNION ALL
SELECT 'readmissions',   COUNT(*) FROM readmissions
ORDER BY table_name;
