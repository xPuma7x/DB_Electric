-- 1. DER ZETTEL (Das hier passiert nur 1x)
WITH mein_zeit_zettel AS (
    SELECT zeit_id FROM dim_zeit WHERE jahr IN (2023, 2024)
)

-- 2. Person A (Lieferanten) nutzt den Zettel
SELECT 
    lf.lieferant_name, 
    AVG(lp.preis_eur_kwh)
FROM fact_lieferantenpreis lp
JOIN dim_lieferant lf ON lp.lieferant_id = lf.lieferant_id
JOIN mein_zeit_zettel z ON lp.zeit_id = z.zeit_id -- < Hier wird der Zettel genutzt
GROUP BY lf.lieferant_name

UNION ALL

-- 3. Person B (Spotmarkt) nutzt DEN GLEICHEN Zettel
SELECT 
    'Spotmarkt', 
    AVG(s.preis_eur_kwh)
FROM fact_spotmarkt s
JOIN mein_zeit_zettel z ON s.zeit_id = z.zeit_id; -- < Hier wird der Zettel nochmal genutzt