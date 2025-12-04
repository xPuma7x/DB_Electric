-- ============================================================
-- FRAGE 1: Stromkostenintensität (CFO)
-- ============================================================
-- Welche Standorte hatten Stückkosten > 15% über Durchschnitt?
-- ============================================================
-- 
-- Diese Query berechnet die Stromkosten pro produziertes Stück für jeden
-- Standort pro Quartal und identifiziert Standorte, die deutlich über
-- dem Durchschnitt liegen.
-- ============================================================

-- Schritt 1: Energieverbrauch pro Standort/Quartal aggregieren
-- Aggregiert den gesamten Stromverbrauch (in kWh) für jeden Standort
-- pro Jahr und Quartal. Berücksichtigt nur gültige Messungen (messstatus = 'OK').
WITH energie_pro_standort AS (
    SELECT 
        z.jahr,                    -- Jahr für Gruppierung
        z.quartal,                 -- Quartal für Gruppierung
        s.standort_id,             -- Standort-ID
        s.standort_name,           -- Standort-Name (für Ausgabe)
        SUM(e.verbrauch_kwh) AS total_kwh  -- Summe aller Verbräuche in kWh
    FROM fact_energie e
    JOIN dim_zeit z ON e.zeit_id = z.zeit_id           -- Zeit-Dimension für Jahr/Quartal
    JOIN dim_linie l ON e.linie_id = l.linie_id        -- Linie → Standort-Zuordnung
    JOIN dim_standort s ON l.standort_id = s.standort_id
    WHERE z.jahr IN (2023, 2024)                       -- Nur relevante Jahre
      AND e.messstatus = 'OK'                          -- Nur gültige Messungen
    GROUP BY z.jahr, z.quartal, s.standort_id, s.standort_name
),

-- Schritt 2: Produktion pro Standort/Quartal aggregieren
-- Berechnet die Gesamtproduktion (Anzahl produzierter Stücke) für jeden
-- Standort pro Jahr und Quartal. Summiert nur "gute" Stücke (menge_gut).
produktion_pro_standort AS (
    SELECT 
        z.jahr,                    -- Jahr für Gruppierung
        z.quartal,                 -- Quartal für Gruppierung
        l.standort_id,             -- Standort-ID
        SUM(p.menge_gut) AS total_stueck  -- Summe aller produzierten Stücke
    FROM fact_produktion p
    JOIN dim_zeit z ON p.zeit_id = z.zeit_id           -- Zeit-Dimension
    JOIN dim_linie l ON p.linie_id = l.linie_id        -- Linie → Standort-Zuordnung
    WHERE z.jahr IN (2023, 2024)                       -- Nur relevante Jahre
    GROUP BY z.jahr, z.quartal, l.standort_id
),

-- Schritt 3: Durchschnittspreis pro Standort/Quartal berechnen
-- Ermittelt den durchschnittlichen Strompreis (€/kWh) für jeden Standort
-- pro Jahr und Quartal. Der Preis kommt von den Lieferantenpreisen,
-- die über Verträge den Standorten zugeordnet sind.
preis_pro_standort AS (
    SELECT 
        z.jahr,                    -- Jahr für Gruppierung
        z.quartal,                 -- Quartal für Gruppierung
        v.standort_id,             -- Standort-ID (über Vertrag)
        AVG(lp.preis_eur_kwh) AS avg_preis  -- Durchschnittspreis in €/kWh
    FROM fact_lieferantenpreis lp
    JOIN dim_zeit z ON lp.zeit_id = z.zeit_id           -- Zeit-Dimension
    JOIN dim_lieferant l ON lp.lieferant_id = l.lieferant_id  -- Lieferant-Info
    JOIN dim_vertrag v ON v.lieferant_id = l.lieferant_id     -- Vertrag → Standort
    WHERE z.jahr IN (2023, 2024)                       -- Nur relevante Jahre
    GROUP BY z.jahr, z.quartal, v.standort_id
),

-- Schritt 4: Stückkosten pro Standort/Quartal berechnen
-- Kombiniert Energieverbrauch, Produktion und Preis, um die
-- Stromkosten pro produziertes Stück zu berechnen.
-- Formel: (Gesamtverbrauch × Durchschnittspreis) / Anzahl Stücke
standort_kosten AS (
    SELECT 
        e.jahr,                    -- Jahr
        e.quartal,                 -- Quartal
        e.standort_name,           -- Standort-Name
        e.total_kwh,               -- Gesamtverbrauch in kWh
        p.total_stueck,            -- Gesamtproduktion in Stück
        pr.avg_preis,              -- Durchschnittspreis in €/kWh
        -- Berechnung: Gesamtkosten geteilt durch Anzahl Stücke
        (e.total_kwh * pr.avg_preis) / p.total_stueck AS kosten_pro_stueck
    FROM energie_pro_standort e
    -- Verknüpfe mit Produktion (muss gleicher Standort, Jahr und Quartal sein)
    JOIN produktion_pro_standort p 
        ON e.standort_id = p.standort_id 
        AND e.jahr = p.jahr
        AND e.quartal = p.quartal
    -- Verknüpfe mit Preis (muss gleicher Standort, Jahr und Quartal sein)
    JOIN preis_pro_standort pr 
        ON e.standort_id = pr.standort_id 
        AND e.jahr = pr.jahr
        AND e.quartal = pr.quartal
),

-- Schritt 5: Durchschnittliche Stückkosten pro Quartal berechnen
-- Berechnet den Durchschnitt aller Standorte pro Jahr und Quartal.
-- Dieser Wert dient als Vergleichsmaßstab für die Abweichung.
durchschnitt AS (
    SELECT 
        jahr,                      -- Jahr für Gruppierung
        quartal,                   -- Quartal für Gruppierung
        AVG(kosten_pro_stueck) AS avg_kosten_pro_stueck  -- Durchschnitt aller Standorte
    FROM standort_kosten
    GROUP BY jahr, quartal
)

-- Schritt 6: Ergebnis: Standorte mit >15% Abweichung vom Durchschnitt
-- Zeigt alle Standorte, deren Stückkosten mehr als 15% über dem
-- Durchschnitt liegen. Sortiert nach Jahr, Quartal und Abweichung (höchste zuerst).
SELECT 
    sk.standort_name,              -- Name des Standorts
    sk.jahr,                       -- Jahr
    sk.quartal,                    -- Quartal
    ROUND(sk.kosten_pro_stueck, 4) AS kosten_pro_stueck_eur,      -- Stückkosten des Standorts
    ROUND(d.avg_kosten_pro_stueck, 4) AS durchschnitt_eur,        -- Durchschnitt aller Standorte
    -- Berechnung der prozentualen Abweichung: ((Standort - Durchschnitt) / Durchschnitt) × 100
    ROUND((sk.kosten_pro_stueck - d.avg_kosten_pro_stueck) / d.avg_kosten_pro_stueck * 100, 1) AS abweichung_pct
FROM standort_kosten sk
-- Verknüpfe mit Durchschnitt (gleiches Jahr und Quartal)
JOIN durchschnitt d ON sk.jahr = d.jahr AND sk.quartal = d.quartal
-- Filter: Nur Standorte mit >15% Abweichung
WHERE (sk.kosten_pro_stueck - d.avg_kosten_pro_stueck) / d.avg_kosten_pro_stueck > 0.15
ORDER BY sk.jahr, sk.quartal, abweichung_pct DESC;  -- Sortierung: Jahr → Quartal → Abweichung (absteigend)