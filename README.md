# DB_Electric – Stromkosten-Analysesystem

**3. Semester Datenbanken WDS24A – Capstone Projekt**

---

## 📋 Projektübersicht

Dieses Projekt entwickelt ein Data-Engineering-System zur Analyse von Stromkosten in einem produzierenden Unternehmen mit 5 Standorten in Deutschland. Das System beantwortet drei datengetriebene Kernfragen für unterschiedliche Stakeholder.

**Technologien:** Python 3.12+, pandas, SQLite, uv

---

## 🎯 Die drei Kernfragen

### Frage 1: Stromkostenintensität (Finanz-Perspektive)

**Kernfrage:** Welche Standorte wiesen im Zeitraum Q1–Q4 2024 strombezogene Stückkosten (€/Einheit) auf, die mehr als 15% über dem unternehmensweiten Durchschnitt lagen, und wie hat sich diese Abweichung quartalsweise entwickelt?

| **Aspekt** | **Spezifikation** |
|---|---|
| **Stakeholder** | CFO (Chief Financial Officer) |
| **Entscheidung** | Priorisierung von Modernisierungsbudgets für "Ausreißer"-Standorte. |
| **Risiko** | Fehlallokation von Investitionsbudget; Ineffizienzen werden übersehen. |
| **Messgrößen** | Stromkosten pro Einheit (€/Stück), Abweichung vom Durchschnitt (%). |
| **Zeitfenster** | 12 Monate (Q1–Q4 2024), quartalsweise aggregiert. |
| **Frequenz** | Quartalsweise (Reporting). |
| **Erfolgskriterium** | Streuung der Stückkosten zwischen Standorten < 10%. |
| **Benötigte Daten** | Produktionsmengen, Energieverbrauch, Vertragspreise (`fact_production`, `fact_energy`). |

### Frage 2: Lastspitzen-Analyse (Operations-Perspektive)

**Kernfrage:** Welche Produktionslinien verursachten in Q4 2024 wiederholt Lastspitzen >500 kW, und in welchen Schichten traten diese gehäuft auf?

| **Aspekt** | **Spezifikation** |
|---|---|
| **Stakeholder** | Produktionsleiter / COO |
| **Entscheidung** | Optimierung der Schichtplanung und Lastverteilung zur Vermeidung von Spitzenlastgebühren. |
| **Risiko** | Hohe Netzentgelte durch unkontrollierte Leistungsspitzen; Produktionsausfälle durch Überlastung. |
| **Messgrößen** | Anzahl Lastspitzen (>500 kW), Durchschnitts-/Max-Leistung (kW), Auslastung (%). |
| **Zeitfenster** | 3 Monate (Q4 2024: Oktober–Dezember), pro Schicht aggregiert. |
| **Frequenz** | Monatlich (Reporting). |
| **Erfolgskriterium** | Linien mit >6 Spitzen pro Quartal identifiziert und Maßnahmen eingeleitet. |
| **Benötigte Daten** | Leistungsmesswerte, Produktionsauslastung (`fact_energie`, `fact_produktion`, `dim_zeit`, `dim_linie`, `dim_standort`). |

### Frage 3: Lieferantenpreis-Analyse (Einkaufs-Perspektive)

**Kernfrage:** Wie haben sich die durchschnittlichen Einkaufspreise (€/kWh) pro Lieferant im Zeitraum 2023–2024 im Vergleich zum Spotmarkt entwickelt, und welche Lieferanten zeigen die geringste Preisvolatilität?

| **Aspekt** | **Spezifikation** |
|---|---|
| **Stakeholder** | CFO / Einkaufsleitung |
| **Entscheidung** | Auswahl und Neuverhandlung von Lieferantenverträgen basierend auf Preis-Risiko-Verhältnis. |
| **Risiko** | Überhöhte Beschaffungskosten; unkalkulierbare Preisschwankungen bei volatilen Lieferanten. |
| **Messgrößen** | Durchschnittspreis (€/kWh), Aufschlag vs. Spotmarkt (€ und %), Volatilität, Variationskoeffizient (%). |
| **Zeitfenster** | 24 Monate (2023–2024), quartalsweise aggregiert. |
| **Frequenz** | Quartalsweise (Reporting). |
| **Erfolgskriterium** | Lieferanten mit Variationskoeffizient <10% und Aufschlag <15% vs. Spotmarkt identifiziert. |
| **Benötigte Daten** | Lieferantenpreise, Spotmarktpreise (`fact_lieferantenpreis`, `fact_spotmarkt`, `dim_zeit`, `dim_lieferant`). |

---

## 📊 Datenmodell

### ER-Diagramm (Star Schema)

```
                    ┌──────────────┐
                    │  dim_zeit    │
                    │──────────────│
                    │ zeit_id (PK) │
                    │ datum        │
                    │ jahr         │
                    │ quartal      │
                    │ monat        │
                    │ kw           │
                    │ stunde       │
                    │ schicht      │
                    │ ist_werktag  │
                    └──────┬───────┘
                           │
    ┌──────────────────────┼──────────────────────┐
    │                      │                      │
    ▼                      ▼                      ▼
┌─────────────┐    ┌─────────────────┐    ┌──────────────────┐
│fact_energie │    │ fact_produktion │    │  fact_spotmarkt  │
│─────────────│    │─────────────────│    │──────────────────│
│ energie_id  │    │ produktion_id   │    │ spot_id          │
│ zeit_id(FK) │    │ zeit_id (FK)    │    │ zeit_id (FK)     │
│ linie_id(FK)│    │ linie_id (FK)   │    │ preis_eur_kwh    │
│ vertrag_id  │    │ menge_gut       │    │ marktgebiet      │
│ verbrauch   │    │ menge_ausschuss │    └──────────────────┘
│ leistung_max│    │ auslastung_pct  │
│ messstatus  │    │ laufzeit_min    │    ┌────────────────────┐
└──────┬──────┘    └────────┬────────┘    │fact_lieferantenpreis│
       │                    │             │────────────────────│
       │                    │             │ preis_id           │
       ▼                    ▼             │ zeit_id (FK)       │
┌──────────────┐    ┌──────────────┐      │ lieferant_id (FK)  │
│  dim_linie   │    │ dim_standort │      │ preis_eur_kwh      │
│──────────────│    │──────────────│      └─────────┬──────────┘
│ linie_id(PK) │───▶│standort_id(PK)│               │
│ standort_id  │    │ standort_code │               ▼
│ linie_code   │    │ standort_name │      ┌──────────────────┐
│ technologie  │    │ land          │      │  dim_lieferant   │
│ nennleistung │    │ region        │      │──────────────────│
└──────────────┘    └───────┬───────┘      │lieferant_id (PK) │
                            │              │ lieferant_code   │
                            ▼              │ lieferant_name   │
                    ┌──────────────┐       │ typ              │
                    │ dim_vertrag  │       └────────┬─────────┘
                    │──────────────│                │
                    │vertrag_id(PK)│◀───────────────┘
                    │lieferant_id  │   n:m Beziehung
                    │standort_id   │
                    │gueltig_ab    │
                    │gueltig_bis   │
                    │grundpreis    │
                    └──────────────┘
```

### Modellierungsentscheidungen

| Entscheidung | Begründung |
|--------------|------------|
| **Star Schema** | Optimiert für analytische Queries mit vielen JOINs |
| **n:m über `dim_vertrag`** | Ein Standort kann mehrere Lieferanten haben (zeitlich begrenzt), ein Lieferant beliefert mehrere Standorte |
| **`dim_zeit` auf 15-Min-Basis** | Entspricht der Granularität von Strompreisen (SMARD-Daten) |
| **`messstatus` in `fact_energie`** | Ermöglicht NULL-Handling und Datenqualitätsanalysen |

### Tabellenübersicht

| Tabelle | Zeilen | Beschreibung |
|---------|-------:|--------------|
| `dim_zeit` | ~70.000 | 15-Min-Intervalle 2023–2024 |
| `dim_standort` | 5 | Produktionsstandorte in DE |
| `dim_linie` | 15 | Produktionslinien (3 pro Standort) |
| `dim_lieferant` | 4 | Stromlieferanten |
| `dim_vertrag` | 6 | Lieferverträge |
| `fact_energie` | ~962.000 | Energieverbrauch pro Intervall/Linie |
| `fact_produktion` | ~28.000 | Produktionsmengen pro Schicht/Linie |
| `fact_spotmarkt` | ~70.000 | Echte SMARD-Großhandelspreise |
| `fact_lieferantenpreis` | ~281.000 | Lieferantenpreise (abgeleitet) |
| **Gesamt** | **~1.400.000** | Large Dataset |

---

## 🔧 Installation & Ausführung

```bash
# Abhängigkeiten installieren (mit uv)
uv sync

# Gesamtes Projekt ausführen (Generierung → Laden → Queries)
uv run main.py

# Oder mit args
uv run main.py --skip-generate --skip-load --visualize

# Oder einzelne Schritte:
uv run src.data_generation.generate_all   # Daten generieren
uv run src.data_loading.load_to_sqlite    # In SQLite laden
uv run src.queries.run_queries            # Queries ausführen
```

---

## 📁 Projektstruktur

```
DB_Electric/
├── main.py                          # Orchestriert alle Schritte
├── pyproject.toml                   # Projektdefinition (uv)
├── uv.lock                          # Lockfile
├── data/
│   ├── create_tables.sql            # DDL-Schema
│   ├── stromkosten.db               # SQLite-Datenbank
│   ├── grosshandelpreise_*.csv      # SMARD-Quelldaten
│   └── generated/                   # Generierte CSV-Dateien
│       ├── dim_*.csv
│       └── fact_*.csv
└── src/
    ├── data_generation/             # Python-Generatoren
    │   ├── generate_all.py
    │   ├── dim_standort.py
    │   ├── dim_linie.py
    │   ├── dim_lieferant.py
    │   ├── dim_vertrag.py
    │   ├── dim_zeit_gen.py
    │   ├── fact_energie.py
    │   ├── fact_production.py
    │   ├── fact_spotmarkt.py
    │   └── fact_lieferantenpreis.py
    ├── data_loading/
    │   └── load_to_sqlite.py        # CSV → SQLite Import
    └── queries/
        ├── run_queries.py           # Query-Runner
        ├── frage1.sql               # Stromkostenintensität
        ├── frage2.sql               # Lastspitzen
        └── frage3.sql               # Lieferantenpreise
```

---

## 📈 SQL-Queries

### Frage 1: Stromkostenintensität

**JOIN-Pfad:** `fact_energie` → `dim_zeit` → `dim_linie` → `dim_standort` (+ Produktion + Preise)

```sql
-- Vereinfachte Struktur
WITH energie_pro_standort AS (...),
     produktion_pro_standort AS (...),
     preis_pro_standort AS (...),
     standort_kosten AS (...),
     durchschnitt AS (...)
SELECT standort_name, kosten_pro_stueck, abweichung_pct
FROM standort_kosten
WHERE abweichung_pct > 15;
```

**Performance:**
- 5 CTEs mit jeweils GROUP BY über ~500k Zeilen
- Indizes auf `zeit_id`, `linie_id` beschleunigen JOINs
- Cold: ~2s, Warm: ~0.5s (SQLite)

### Frage 2: Lastspitzen

**JOIN-Pfad:** `fact_energie` → `dim_zeit` → `dim_linie` → `dim_standort`

```sql
WITH lastspitzen AS (
    SELECT ... WHERE leistung_max_kw > 500
),
auslastung AS (...)
SELECT standort_name, linie_code, COUNT(*) AS anzahl_spitzen
HAVING COUNT(*) > 6;
```

### Frage 3: Lieferantenpreise

**JOIN-Pfad:** `fact_lieferantenpreis` → `dim_zeit` → `dim_lieferant` (+ Spotmarkt)

```sql
WITH lieferant_quartalspreise AS (...),
     spot_quartalspreise AS (...),
     volatilitaet AS (
         SELECT SQRT(AVG(x²) - AVG(x)²) AS volatilitaet ...
     )
SELECT lieferant_name, avg_preis, aufschlag_pct, volatilitaet;
```

---

## ⚠️ Datenqualität & NULL-Handling

### NULL-Werte in `fact_energie`

Die Spalte `messstatus` enthält drei Werte:
- `OK` (95%): Gültige Messung
- `FEHLER` (5%): Defekter Sensor oder fehlende Werte

**Beispiel aus den Queries:**
```sql
-- Frage 1: Nur valide Messungen verwenden
WHERE e.messstatus = 'OK'

-- Frage 2: Nur valide Messungen
WHERE e.messstatus = 'OK'
```

**Relevanz:** In echten Systemen können Sensorfehler, Netzausfälle oder Wartungsfenster zu NULL-Werten führen. Ohne korrekte Filterung würden Aggregationen verfälscht (z.B. falscher Durchschnitt durch Division mit weniger Zeilen).

---

## 🆚 MongoDB-Vergleich (Theoretisch)

**Beispielfrage:** „Wie viele Eskalations-Events pro Projekt gab es im letzten Monat – gruppiert nach Typ?"

### JSON-Beispielobjekt

```json
{
  "_id": "evt_20241205_001",
  "projekt_id": "PRJ-2024-042",
  "timestamp": "2024-12-05T14:32:00Z",
  "typ": "LASTSPITZE",
  "details": {
    "linie_id": "MUC-L2",
    "peak_kw": 612.5,
    "grenzwert_kw": 500,
    "dauer_sekunden": 45
  },
  "eskalation": {
    "stufe": 2,
    "benachrichtigt": ["ops@firma.de", "coo@firma.de"],
    "status": "acknowledged"
  }
}
```

### Warum SQL schwierig ist

Verschachtelte Objekte wie `details` und `eskalation` erfordern in SQL entweder zusätzliche Tabellen (n:m) oder JSON-Spalten, was die Abfrage verkompliziert und Performance-Probleme bei häufigen Schema-Änderungen verursacht.

### Warum MongoDB geeigneter wäre

Dokumentenorientierte Speicherung erlaubt flexible Event-Strukturen, native Array-Operationen für `benachrichtigt[]`, und die Aggregation Pipeline ist für Event-Gruppierungen optimiert.

### JSON-Schema

```json
{
  "bsonType": "object",
  "required": ["projekt_id", "timestamp", "typ"],
  "properties": {
    "typ": { "enum": ["LASTSPITZE", "SENSOR_AUSFALL", "PREIS_SPIKE"] },
    "eskalation.stufe": { "bsonType": "int", "minimum": 1, "maximum": 3 }
  }
}
```

---

## 📊 Executive Summary

### Kernfragen & Erkenntnisse

| Frage | Insight |
|-------|---------|
| **Stromkostenintensität** | Hamburg-Harburg liegt konstant >15% über dem Durchschnitt durch niedrigere Produktionseffizienz bei höherem Verbrauch |
| **Lastspitzen** | München-Garching (MUC-L1, MUC-L2) verursacht 3× mehr Lastspitzen – korreliert mit Spätschicht-Auslastung |
| **Lieferantenpreise** | Spotmarkt-Direkt bietet günstigste Preise, aber höchste Volatilität (5%); Naturstrom ist 20% teurer, aber stabilste Preise |

### Limitierungen

- Keine echten Produktionsdaten (synthetisch generiert)
- SQLite ohne echte Concurrent-Workload-Tests
- Keine saisonalen Muster in Produktion modelliert

### Empfehlung

1. **Hamburg:** Energieaudit durchführen, Maschinen-Retrofit prüfen
2. **München:** Lastmanagement für Spätschicht implementieren (Load Shifting)
3. **Einkauf:** Hybrid-Modell evaluieren – 70% Festpreis (E.ON), 30% Spotmarkt für Flexibilität

---

## 👥 Team

WDS24A – Datenbanken, 3. Semester
