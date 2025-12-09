-- ============================================================
-- FRAGE 3: Lieferantenpreis-Analyse (CTE Optimiert)
-- ============================================================
WITH 
-- 1. Der "Scope": Einmal definiert, überall genutzt (DRY Prinzip)
-- Performance-Vorteil: Der Zeit-Index wird nur 1x gescannt.
relevante_zeit AS (
    SELECT zeit_id, jahr 
    FROM dim_zeit 
    WHERE jahr IN (2023, 2024)
),

-- 2. Aggregation Lieferanten (Nur im Scope)
lieferanten_agg AS (
    SELECT 
        lp.lieferant_id,
        AVG(lp.preis_eur_kwh) as ist_preis
    FROM fact_lieferantenpreis lp
    JOIN relevante_zeit rz ON lp.zeit_id = rz.zeit_id
    GROUP BY lp.lieferant_id
),

-- 3. Aggregation Markt (Nur im Scope)
markt_agg AS (
    SELECT 
        AVG(s.preis_eur_kwh) as markt_preis
    FROM fact_spotmarkt s
    JOIN relevante_zeit rz ON s.zeit_id = rz.zeit_id
)

-- 4. Der Vergleich (JOIN statt UNION)
SELECT 
    l.lieferant_name,
    l.typ,
    ROUND(la.ist_preis, 4) as unser_preis,
    ROUND(ma.markt_preis, 4) as markt_referenz,
    
    -- Der eigentliche Mehrwert: Die Berechnung des Aufschlags (Delta)
    ROUND(la.ist_preis - ma.markt_preis, 4) as aufschlag_eur,
    ROUND(((la.ist_preis - ma.markt_preis) / ma.markt_preis) * 100, 1) || '%' as aufschlag_prozent

FROM lieferanten_agg la
JOIN dim_lieferant l ON la.lieferant_id = l.lieferant_id
CROSS JOIN markt_agg ma -- Da Markt nur 1 Zeile ist, ist Cross Join okay
ORDER BY aufschlag_eur DESC;