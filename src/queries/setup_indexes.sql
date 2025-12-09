-- ============================================================
-- Benchmark-Indizes (einmalig vor Tests ausführen)
-- ============================================================

-- Partieller Index für Lastspitzen-Filter (Frage 2)
CREATE INDEX IF NOT EXISTS idx_energie_leistung 
    ON fact_energie(leistung_max_kw) 
    WHERE leistung_max_kw > 500;

