-- Der "Naive" Ansatz: Subqueries im SELECT
SELECT 
    s.standort_name,
    
    -- 1. Hole Energie (Hauptabfrage / Äußere Schleife)
    -- Hier definiert die DB die "Taktung". Wenn du 5 Standorte hast, 
    -- iteriert die DB hier 5 mal (Zeile für Zeile).
    SUM(e.verbrauch_kwh) AS gesamt_energie,
    
    -- 2. Hole Menge (Subquery pro Zeile! -> DER KILLER)
    -- PERFORMANCE PROBLEM: "Nested Loop"
    -- Die Datenbank muss hier für JEDE Zeile der Hauptabfrage (also 5x) 
    -- diese komplette Unter-Abfrage neu starten. 
    -- Bei 5 Standorten okay, bei 50.000 Zeilen friert das System ein.
    (
        SELECT SUM(p.menge_gut) 
        FROM fact_produktion p
        JOIN dim_linie l2 ON p.linie_id = l2.linie_id
        JOIN dim_zeit z2 ON p.zeit_id = z2.zeit_id
        
        -- ↓↓↓ DAS GIFT (Korrelation) ↓↓↓
        -- Da "s.standort_id" von DRAUSSEN kommt, kann die DB diese Query 
        -- nicht einmalig vorab berechnen. Sie muss warten, bis die äußere 
        -- Schleife bei Standort X ist, um dann spezifisch für X zu suchen.
        -- Das verhindert effiziente "Hash Joins" (Massenverarbeitung).
        WHERE l2.standort_id = s.standort_id 
          AND z2.jahr = 2024
    ) AS gesamt_menge,
    
    -- 3. Hole Preis (Subquery pauschal -> OKAY)
    -- PERFORMANCE CHECK: Unkorreliert
    -- Hier gibt es KEINE Abhängigkeit nach draußen (kein "s.irgendwas").
    -- Die DB ist schlau: Sie führt das GENAU EINMAL aus, merkt sich 
    -- das Ergebnis (z.B. "0.15") und klebt es einfach an jede Zeile dran.
    (
        SELECT AVG(lp.preis_eur_kwh)
        FROM fact_lieferantenpreis lp
        JOIN dim_zeit z3 ON lp.zeit_id = z3.zeit_id
        WHERE z3.jahr = 2024
    ) AS durchschnittspreis

FROM fact_energie e
JOIN dim_zeit z ON e.zeit_id = z.zeit_id
JOIN dim_linie l ON e.linie_id = l.linie_id
JOIN dim_standort s ON l.standort_id = s.standort_id
WHERE z.jahr = 2024 
  AND e.messstatus = 'OK'
GROUP BY s.standort_id, s.standort_name;