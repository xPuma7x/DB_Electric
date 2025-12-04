-- ============================================================
-- FRAGE 2: Lastspitzen-Analyse (COO)
-- ============================================================
WITH lastspitzen AS (
    SELECT 
        z.datum,
        z.stunde,
        z.schicht,
        l.linie_id,
        l.linie_code,
        l.linie_name,
        s.standort_name,
        e.leistung_max_kw
    FROM fact_energie e
    JOIN dim_zeit z ON e.zeit_id = z.zeit_id
    JOIN dim_linie l ON e.linie_id = l.linie_id
    JOIN dim_standort s ON l.standort_id = s.standort_id
    WHERE z.jahr = 2024
      AND z.monat IN (10, 11, 12)
      AND e.leistung_max_kw > 500
      AND e.messstatus != 'NULL'
),

auslastung AS (
    SELECT 
        z.datum,
        z.schicht,
        l.linie_id,
        AVG(p.auslastung_pct) AS avg_auslastung
    FROM fact_produktion p
    JOIN dim_zeit z ON p.zeit_id = z.zeit_id
    JOIN dim_linie l ON p.linie_id = l.linie_id
    WHERE z.jahr = 2024 AND z.monat IN (10, 11, 12)
)

SELECT 
    lp.standort_name,
    lp.linie_code,
    lp.linie_name,
    lp.schicht,
    COUNT(*) AS anzahl_spitzen,
    ROUND(AVG(lp.leistung_max_kw), 1) AS avg_peak_kw,
    ROUND(MAX(lp.leistung_max_kw), 1) AS max_peak_kw,
    ROUND(a.avg_auslastung, 1) AS auslastung_pct
FROM lastspitzen lp
LEFT JOIN auslastung a 
    ON lp.linie_id = a.linie_id 
    AND lp.schicht = a.schicht
GROUP BY 
    lp.standort_name, 
    lp.linie_code, 
    lp.linie_name, 
    lp.schicht,
    a.avg_auslastung
HAVING COUNT(*) > 6           -- Nur Problemfälle
ORDER BY anzahl_spitzen DESC
LIMIT 10;                     -- Top 10