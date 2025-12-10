-- ============================================================
-- FRAGE 2: Lastspitzen-Analyse (MIT INDEX)
-- Voraussetzung: idx_energie_leistung (siehe setup_indexes.sql)
-- ============================================================
SELECT 
    s.standort_name,
    l.linie_code,
    z.schicht,
    COUNT(*) AS anzahl_spitzen,
    ROUND(MAX(e.leistung_max_kw), 1) AS max_peak_kw

FROM fact_energie e
JOIN dim_zeit z ON e.zeit_id = z.zeit_id
JOIN dim_linie l ON e.linie_id = l.linie_id
JOIN dim_standort s ON l.standort_id = s.standort_id

WHERE z.jahr = 2024
  AND z.monat IN (10, 11, 12)
  AND e.leistung_max_kw > 500
  AND e.messstatus = 'OK'

GROUP BY s.standort_name, l.linie_code, z.schicht
HAVING COUNT(*) > 6
ORDER BY anzahl_spitzen DESC
LIMIT 10;
