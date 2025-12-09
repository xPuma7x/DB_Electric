-- Lieferantenpreise
SELECT 
    lf.lieferant_name AS name,
    ROUND(AVG(lp.preis_eur_kwh), 4) AS avg_preis_eur_kwh
FROM fact_lieferantenpreis lp
JOIN dim_lieferant lf ON lp.lieferant_id = lf.lieferant_id
JOIN dim_zeit z ON lp.zeit_id = z.zeit_id
WHERE z.jahr IN (2023, 2024)
GROUP BY lf.lieferant_name


UNION ALL
-- Klebt beide Ergebnisse zusammen (wie Copy-Paste untereinander)
-- Ohne UNION müssten wir 2 separate Queries machen

-- Spotmarkt als Referenz
SELECT 
    'SPOTMARKT (Benchmark)' AS name,
    ROUND(AVG(s.preis_eur_kwh), 4) AS avg_preis_eur_kwh
FROM fact_spotmarkt s
JOIN dim_zeit z ON s.zeit_id = z.zeit_id
WHERE z.jahr IN (2023, 2024);
