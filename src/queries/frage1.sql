-- Frage: Welche Standorte wiesen in Q1–Q4 2024 strombezogene Stückkosten (€/Einheit) 
--        über 15% des unternehmensweiten Durchschnitts auf?

-- ══════════════════════════════════════════════════════════════════════════════
-- AUFBAU: Basis → Anreicherung → Filter → Gruppierung → Aggregation
-- ══════════════════════════════════════════════════════════════════════════════

SELECT 
    -- 1. Direkt aus JOIN: Standortname
    s.standort_name,
    
    -- 2. Aggregation Hauptquery: Gesamtenergie pro Standort
    SUM(e.verbrauch_kwh) AS gesamt_energie,
    
    -- 3. Subquery: Produktionsmenge aus separater Faktentabelle
    --    Korreliert mit Standort der Hauptquery (s.standort_id)
    (
        SELECT SUM(p.menge_gut) 
        FROM fact_produktion p
        JOIN dim_linie l2 ON p.linie_id = l2.linie_id
        JOIN dim_zeit z2 ON p.zeit_id = z2.zeit_id
        WHERE l2.standort_id = s.standort_id 
          AND z2.jahr = 2024
    ) AS gesamt_menge,
    
    -- 4. Subquery: Durchschnittspreis (unternehmensweit, nicht korreliert)
    (
        SELECT AVG(lp.preis_eur_kwh)
        FROM fact_lieferantenpreis lp
        JOIN dim_zeit z3 ON lp.zeit_id = z3.zeit_id
        WHERE z3.jahr = 2024
    ) AS durchschnittspreis

-- ══════════════════════════════════════════════════════════════════════════════
-- BASIS: fact_energie als Ausgangspunkt (Messwerte)
-- ══════════════════════════════════════════════════════════════════════════════
FROM fact_energie e

-- ANREICHERUNG: Dimensionstabellen für Kontext
JOIN dim_zeit z ON e.zeit_id = z.zeit_id           -- Wann?
JOIN dim_linie l ON e.linie_id = l.linie_id        -- Welche Linie?
JOIN dim_standort s ON l.standort_id = s.standort_id  -- Welcher Standort?

-- FILTER: Nur gültige Messungen aus 2024
WHERE z.jahr = 2024 
  AND e.messstatus = 'OK'

-- GRUPPIERUNG: Aggregation auf Standort-Ebene → 5 Ergebniszeilen
GROUP BY s.standort_id, s.standort_name;