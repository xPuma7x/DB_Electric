-- CTE Ansatz: Erst alles berechnen, dann zusammenfügen
WITH 
-- A: Strompreis (Skalar, 1x berechnen)
strompreis AS (
    SELECT AVG(lp.preis_eur_kwh) as avg_preis
    FROM fact_lieferantenpreis lp
    JOIN dim_zeit z ON lp.zeit_id = z.zeit_id
    WHERE z.jahr = 2024
),

-- B: Energie pro Standort (Mengen-Operation: Alle auf einmal)
energie_agg AS (
    SELECT 
        l.standort_id, 
        s.standort_name,
        SUM(e.verbrauch_kwh) AS gesamt_energie
    FROM fact_energie e
    JOIN dim_zeit z ON e.zeit_id = z.zeit_id
    JOIN dim_linie l ON e.linie_id = l.linie_id
    JOIN dim_standort s ON l.standort_id = s.standort_id
    WHERE z.jahr = 2024 AND e.messstatus = 'OK'
    GROUP BY l.standort_id, s.standort_name
),

-- C: Produktion pro Standort (Mengen-Operation: Alle auf einmal)
prod_agg AS (
    SELECT 
        l.standort_id,
        SUM(p.menge_gut) AS gesamt_menge
    FROM fact_produktion p
    JOIN dim_zeit z ON p.zeit_id = z.zeit_id
    JOIN dim_linie l ON p.linie_id = l.linie_id
    WHERE z.jahr = 2024
    GROUP BY l.standort_id
)

-- D: Das Finale (Hash Join statt Loop)
SELECT 
    ea.standort_name,
    ea.gesamt_energie,
    pa.gesamt_menge,
    sp.avg_preis
FROM energie_agg ea
LEFT JOIN prod_agg pa ON ea.standort_id = pa.standort_id -- ← Der Join passiert hier im Speicher
CROSS JOIN strompreis sp;