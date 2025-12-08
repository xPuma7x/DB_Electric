-- ============================================================
-- FRAGE 3: Lieferantenpreis-Analyse (Einkauf)
-- ============================================================
-- Ziel: Wie teuer sind unsere Lieferanten vs. Spotmarkt?
-- ============================================================

-- Lieferantenpreise + Spotmarkt-Benchmark in einer Query (UNION)
SELECT 
    lf.lieferant_name AS name,
    lf.typ,
    ROUND(AVG(lp.preis_eur_kwh), 4) AS avg_preis_eur_kwh,
    COUNT(*) AS anzahl_messungen

FROM fact_lieferantenpreis lp
JOIN dim_lieferant lf ON lp.lieferant_id = lf.lieferant_id
JOIN dim_zeit z ON lp.zeit_id = z.zeit_id

WHERE z.jahr IN (2023, 2024)

GROUP BY lf.lieferant_id, lf.lieferant_name, lf.typ

UNION ALL

-- Spotmarkt als Benchmark (zum Vergleich)
SELECT 
    'SPOTMARKT (Benchmark)' AS name,
    'Referenz' AS typ,
    ROUND(AVG(s.preis_eur_kwh), 4) AS avg_preis_eur_kwh,
    COUNT(*) AS anzahl_messungen

FROM fact_spotmarkt s
JOIN dim_zeit z ON s.zeit_id = z.zeit_id

WHERE z.jahr IN (2023, 2024)

ORDER BY avg_preis_eur_kwh;
