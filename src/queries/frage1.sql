-- ============================================================
-- FRAGE 1: Stromkostenintensität (CFO)
-- ============================================================
-- Ziel: Welche Standorte haben Stückkosten >15% über Durchschnitt?
-- 
-- Ansatz (einfach erklärt):
--   1. Energie pro Standort summieren
--   2. Produktion pro Standort summieren  
--   3. Preis pro Standort ermitteln
--   4. Stückkosten = (Energie × Preis) / Produktion
--   5. Mit Durchschnitt vergleichen
-- ============================================================

-- Schritt 1: Gesamtverbrauch und Kosten pro Standort im Jahr 2024
SELECT 
    s.standort_name,
    
    -- Summe Energieverbrauch (kWh)
    SUM(e.verbrauch_kwh) AS verbrauch_kwh,
    
    -- Summe Produktionsmenge (aus Subquery, da andere Tabelle)
    (
        SELECT SUM(p.menge_gut) 
        FROM fact_produktion p
        JOIN dim_linie l2 ON p.linie_id = l2.linie_id
        JOIN dim_zeit z2 ON p.zeit_id = z2.zeit_id
        WHERE l2.standort_id = s.standort_id
          AND z2.jahr = 2024
    ) AS menge_stueck,
    
    -- Durchschnittlicher Strompreis (vereinfacht: erster Lieferant)
    (
        SELECT AVG(lp.preis_eur_kwh)
        FROM fact_lieferantenpreis lp
        JOIN dim_zeit z3 ON lp.zeit_id = z3.zeit_id
        WHERE z3.jahr = 2024
    ) AS avg_preis_eur_kwh

FROM fact_energie e
JOIN dim_zeit z ON e.zeit_id = z.zeit_id
JOIN dim_linie l ON e.linie_id = l.linie_id
JOIN dim_standort s ON l.standort_id = s.standort_id

WHERE z.jahr = 2024
  AND e.messstatus = 'OK'

GROUP BY s.standort_id, s.standort_name
ORDER BY s.standort_name;


-- ============================================================
-- AUSWERTUNG (manuell oder in separater Query):
-- 
-- Stückkosten berechnen:
--   kosten_pro_stueck = (verbrauch_kwh × avg_preis_eur_kwh) / menge_stueck
--
-- Dann: Welche Standorte sind >15% über dem Durchschnitt?
-- ============================================================
