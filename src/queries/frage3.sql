-- ============================================================
-- FRAGE 3: Lieferantenpreis-Analyse (CFO/Einkauf)
-- ============================================================
-- Wie haben sich die durchschnittlichen Einkaufspreise (€/kWh) 
-- pro Lieferant im Zeitraum 2023–2024 im Vergleich zum Spotmarkt 
-- entwickelt, und welche Lieferanten zeigen die geringste Preisvolatilität?
-- ============================================================

-- Durchschnittliche Lieferantenpreise pro Quartal
WITH lieferant_quartalspreise AS (
    SELECT 
        l.lieferant_id,
        l.lieferant_name,
        z.jahr,
        z.quartal,
        AVG(lp.preis_eur_kwh) AS avg_preis,
        COUNT(*) AS anzahl_messungen
    FROM fact_lieferantenpreis lp
    JOIN dim_lieferant l ON lp.lieferant_id = l.lieferant_id
    JOIN dim_zeit z ON lp.zeit_id = z.zeit_id
    WHERE z.jahr IN (2023, 2024)
    GROUP BY l.lieferant_id, l.lieferant_name, z.jahr, z.quartal
),

-- Durchschnittliche Spotmarktpreise pro Quartal
spot_quartalspreise AS (
    SELECT 
        z.jahr,
        z.quartal,
        AVG(s.preis_eur_kwh) AS avg_spot_preis
    FROM fact_spotmarkt s
    JOIN dim_zeit z ON s.zeit_id = z.zeit_id
    WHERE z.jahr IN (2023, 2024)
    GROUP BY z.jahr, z.quartal
),

-- Volatilität pro Lieferant (Gesamtzeitraum) - manuelle Berechnung für SQLite
-- Std = SQRT(AVG(x²) - AVG(x)²)
volatilitaet AS (
    SELECT 
        l.lieferant_id,
        l.lieferant_name,
        AVG(lp.preis_eur_kwh) AS avg_gesamtpreis,
        SQRT(AVG(lp.preis_eur_kwh * lp.preis_eur_kwh) - AVG(lp.preis_eur_kwh) * AVG(lp.preis_eur_kwh)) AS volatilitaet
    FROM fact_lieferantenpreis lp
    JOIN dim_lieferant l ON lp.lieferant_id = l.lieferant_id
    JOIN dim_zeit z ON lp.zeit_id = z.zeit_id
    WHERE z.jahr IN (2023, 2024)
    GROUP BY l.lieferant_id, l.lieferant_name
)

-- Ergebnis: Preisentwicklung pro Lieferant vs. Spotmarkt + Volatilität
SELECT 
    lq.lieferant_name,
    lq.jahr,
    lq.quartal,
    ROUND(lq.avg_preis, 4) AS avg_preis_eur_kwh,
    ROUND(sq.avg_spot_preis, 4) AS avg_spot_eur_kwh,
    ROUND((lq.avg_preis - sq.avg_spot_preis), 4) AS aufschlag_eur_kwh,
    ROUND((lq.avg_preis - sq.avg_spot_preis) / sq.avg_spot_preis * 100, 1) AS aufschlag_pct,
    ROUND(v.volatilitaet, 4) AS volatilitaet,
    ROUND(v.volatilitaet / v.avg_gesamtpreis * 100, 1) AS variationskoeff_pct
FROM lieferant_quartalspreise lq
JOIN spot_quartalspreise sq 
    ON lq.jahr = sq.jahr AND lq.quartal = sq.quartal
JOIN volatilitaet v 
    ON lq.lieferant_id = v.lieferant_id
ORDER BY v.volatilitaet / v.avg_gesamtpreis ASC, lq.jahr, lq.quartal;
