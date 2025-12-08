-- ============================================================
-- FRAGE 2: Lastspitzen-Analyse (Produktionsleiter)
-- ============================================================
-- Ziel: Welche Linien hatten in Q4/2024 oft Lastspitzen >500 kW?
--
-- Ansatz:
--   1. Alle Messungen mit >500 kW finden
--   2. Nach Linie und Schicht gruppieren
--   3. Zählen wie oft das passiert ist
-- ============================================================

SELECT 
    -- Standort und Linie identifizieren
    s.standort_name,
    l.linie_code,
    l.linie_name,
    z.schicht,
    
    -- Wie viele Spitzen gab es?
    COUNT(*) AS anzahl_spitzen,
    
    -- Durchschnittliche Spitzenleistung
    ROUND(AVG(e.leistung_max_kw), 1) AS avg_peak_kw,
    
    -- Maximale Spitzenleistung
    ROUND(MAX(e.leistung_max_kw), 1) AS max_peak_kw

FROM fact_energie e

-- Verknüpfungen zu den Dimensionstabellen
JOIN dim_zeit z ON e.zeit_id = z.zeit_id
JOIN dim_linie l ON e.linie_id = l.linie_id
JOIN dim_standort s ON l.standort_id = s.standort_id

-- Filter: Q4 2024, nur Spitzen über 500 kW, nur gültige Messungen
WHERE z.jahr = 2024
  AND z.monat IN (10, 11, 12)          -- Oktober, November, Dezember
  AND e.leistung_max_kw > 500          -- Nur echte Lastspitzen
  AND e.messstatus = 'OK'              -- Nur valide Sensordaten

-- Gruppierung: Pro Standort, Linie und Schicht
GROUP BY 
    s.standort_name, 
    l.linie_code, 
    l.linie_name, 
    z.schicht

-- Nur Problemfälle zeigen (mehr als 6 Spitzen im Quartal)
HAVING COUNT(*) > 6

-- Sortierung: Schlimmste zuerst
ORDER BY anzahl_spitzen DESC

-- Nur Top 10
LIMIT 10;
