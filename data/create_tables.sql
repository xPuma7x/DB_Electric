-- ============================================================
-- STROMKOSTEN-ANALYSE: SQLite DDL
-- ============================================================

-- Alte Tabellen löschen (falls vorhanden)
DROP TABLE IF EXISTS fact_lieferantenpreis;
DROP TABLE IF EXISTS fact_spotmarkt;
DROP TABLE IF EXISTS fact_energie;
DROP TABLE IF EXISTS fact_produktion;
DROP TABLE IF EXISTS dim_vertrag;
DROP TABLE IF EXISTS dim_linie;
DROP TABLE IF EXISTS dim_lieferant;
DROP TABLE IF EXISTS dim_standort;
DROP TABLE IF EXISTS dim_zeit;


-- ============================================================
-- DIMENSIONEN
-- ============================================================

CREATE TABLE dim_zeit (
    zeit_id         INTEGER PRIMARY KEY,
    datum           TEXT NOT NULL,
    jahr            INTEGER NOT NULL,
    quartal         INTEGER NOT NULL,
    monat           INTEGER NOT NULL,
    kw              INTEGER NOT NULL,
    tag_im_monat    INTEGER NOT NULL,
    stunde          INTEGER NOT NULL,
    intervall_15min INTEGER NOT NULL,
    schicht         TEXT NOT NULL,
    ist_werktag     INTEGER NOT NULL
);

CREATE TABLE dim_standort (
    standort_id     INTEGER PRIMARY KEY,
    standort_code   TEXT NOT NULL UNIQUE,
    standort_name   TEXT NOT NULL,
    land            TEXT NOT NULL,
    region          TEXT NOT NULL
);

CREATE TABLE dim_linie (
    linie_id        INTEGER PRIMARY KEY,
    standort_id     INTEGER NOT NULL,
    linie_code      TEXT NOT NULL UNIQUE,
    linie_name      TEXT NOT NULL,
    technologie     TEXT NOT NULL,
    nennleistung_kw REAL NOT NULL,
    FOREIGN KEY (standort_id) REFERENCES dim_standort(standort_id)
);

CREATE TABLE dim_lieferant (
    lieferant_id    INTEGER PRIMARY KEY,
    lieferant_code  TEXT NOT NULL UNIQUE,
    lieferant_name  TEXT NOT NULL,
    typ             TEXT NOT NULL
);

CREATE TABLE dim_vertrag (
    vertrag_id          INTEGER PRIMARY KEY,
    lieferant_id        INTEGER NOT NULL,
    standort_id         INTEGER NOT NULL,
    vertragsnummer      TEXT NOT NULL UNIQUE,
    gueltig_ab          TEXT NOT NULL,
    gueltig_bis         TEXT NOT NULL,
    grundpreis_eur_monat REAL NOT NULL,
    FOREIGN KEY (lieferant_id) REFERENCES dim_lieferant(lieferant_id),
    FOREIGN KEY (standort_id) REFERENCES dim_standort(standort_id)
);


-- ============================================================
-- FAKTEN
-- ============================================================

CREATE TABLE fact_produktion (
    produktion_id    INTEGER PRIMARY KEY,
    zeit_id          INTEGER NOT NULL,
    linie_id         INTEGER NOT NULL,
    menge_gut        REAL NOT NULL,
    menge_ausschuss  REAL NOT NULL,
    auslastung_pct   REAL NOT NULL,
    laufzeit_minuten INTEGER NOT NULL,
    FOREIGN KEY (zeit_id) REFERENCES dim_zeit(zeit_id),
    FOREIGN KEY (linie_id) REFERENCES dim_linie(linie_id)
);

CREATE TABLE fact_energie (
    energie_id      INTEGER PRIMARY KEY,
    zeit_id         INTEGER NOT NULL,
    linie_id        INTEGER NOT NULL,
    vertrag_id      INTEGER,
    verbrauch_kwh   REAL,
    leistung_max_kw REAL,
    messstatus      TEXT,
    FOREIGN KEY (zeit_id) REFERENCES dim_zeit(zeit_id),
    FOREIGN KEY (linie_id) REFERENCES dim_linie(linie_id),
    FOREIGN KEY (vertrag_id) REFERENCES dim_vertrag(vertrag_id)
);

CREATE TABLE fact_spotmarkt (
    spot_id       INTEGER PRIMARY KEY,
    zeit_id       INTEGER NOT NULL,
    preis_eur_kwh REAL NOT NULL,
    marktgebiet   TEXT NOT NULL,
    FOREIGN KEY (zeit_id) REFERENCES dim_zeit(zeit_id)
);

CREATE TABLE fact_lieferantenpreis (
    preis_id      INTEGER PRIMARY KEY,
    zeit_id       INTEGER NOT NULL,
    lieferant_id  INTEGER NOT NULL,
    preis_eur_kwh REAL NOT NULL,
    FOREIGN KEY (zeit_id) REFERENCES dim_zeit(zeit_id),
    FOREIGN KEY (lieferant_id) REFERENCES dim_lieferant(lieferant_id)
);


-- ============================================================
-- INDIZES (Performance)
-- ============================================================

CREATE INDEX idx_zeit_jahr_quartal ON dim_zeit(jahr, quartal);
CREATE INDEX idx_zeit_jahr_monat ON dim_zeit(jahr, monat);
CREATE INDEX idx_linie_standort ON dim_linie(standort_id);
CREATE INDEX idx_vertrag_lieferant ON dim_vertrag(lieferant_id);
CREATE INDEX idx_vertrag_standort ON dim_vertrag(standort_id);
CREATE INDEX idx_produktion_zeit ON fact_produktion(zeit_id);
CREATE INDEX idx_produktion_linie ON fact_produktion(linie_id);
CREATE INDEX idx_energie_zeit ON fact_energie(zeit_id);
CREATE INDEX idx_energie_linie ON fact_energie(linie_id);
CREATE INDEX idx_spotmarkt_zeit ON fact_spotmarkt(zeit_id);
CREATE INDEX idx_liefpreis_zeit ON fact_lieferantenpreis(zeit_id);
CREATE INDEX idx_liefpreis_lieferant ON fact_lieferantenpreis(lieferant_id);