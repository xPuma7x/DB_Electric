-- ---------------------------------------------------------
-- DIMENSION: Zeit
-- ---------------------------------------------------------
CREATE TABLE dim_zeit (
    zeit_id SERIAL PRIMARY KEY,
    datum DATE NOT NULL,
    jahr INT NOT NULL,
    quartal INT NOT NULL,
    monat INT NOT NULL,
    kw INT NOT NULL,
    tag_im_monat INT NOT NULL,
    stunde INT,
    intervall_15min INT,
    schicht VARCHAR(20),
    ist_werktag BOOLEAN
);

-- ---------------------------------------------------------
-- DIMENSION: Standort
-- ---------------------------------------------------------
CREATE TABLE dim_standort (
    standort_id SERIAL PRIMARY KEY,
    standort_code VARCHAR(50) UNIQUE NOT NULL,
    standort_name VARCHAR(100),
    land VARCHAR(50),
    region VARCHAR(50)
);

-- ---------------------------------------------------------
-- DIMENSION: Linie
-- ---------------------------------------------------------
CREATE TABLE dim_linie (
    linie_id SERIAL PRIMARY KEY,
    standort_id INT REFERENCES dim_standort(standort_id),
    linie_code VARCHAR(50) UNIQUE NOT NULL,
    linie_name VARCHAR(100),
    technologie VARCHAR(100),
    nennleistung_kw DECIMAL(10,2)
);

-- ---------------------------------------------------------
-- DIMENSION: Lieferant
-- ---------------------------------------------------------
CREATE TABLE dim_lieferant (
    lieferant_id SERIAL PRIMARY KEY,
    lieferant_code VARCHAR(50) UNIQUE NOT NULL,
    lieferant_name VARCHAR(100),
    typ VARCHAR(20)
);

-- ---------------------------------------------------------
-- DIMENSION: Vertrag (Bridge Tabelle)
-- ---------------------------------------------------------
CREATE TABLE dim_vertrag (
    vertrag_id SERIAL PRIMARY KEY,
    lieferant_id INT REFERENCES dim_lieferant(lieferant_id),
    standort_id INT REFERENCES dim_standort(standort_id),
    vertragsnummer VARCHAR(100),
    gueltig_ab DATE,
    gueltig_bis DATE,
    grundpreis_eur_monat DECIMAL(10,2)
);

-- ---------------------------------------------------------
-- FACT: Produktion
-- ---------------------------------------------------------
CREATE TABLE fact_produktion (
    produktion_id SERIAL PRIMARY KEY,
    zeit_id INT REFERENCES dim_zeit(zeit_id),
    linie_id INT REFERENCES dim_linie(linie_id),
    menge_gut DECIMAL(12,3),
    menge_ausschuss DECIMAL(12,3),
    auslastung_pct DECIMAL(5,2),
    laufzeit_minuten INT
);

-- ---------------------------------------------------------
-- FACT: Energie
-- ---------------------------------------------------------
CREATE TABLE fact_energie (
    energie_id SERIAL PRIMARY KEY,
    zeit_id INT REFERENCES dim_zeit(zeit_id),
    linie_id INT REFERENCES dim_linie(linie_id),
    vertrag_id INT REFERENCES dim_vertrag(vertrag_id),
    verbrauch_kwh DECIMAL(12,3),
    leistung_max_kw DECIMAL(12,3),
    messstatus VARCHAR(20)
);

-- ---------------------------------------------------------
-- FACT: Spotmarkt
-- ---------------------------------------------------------
CREATE TABLE fact_spotmarkt (
    spot_id SERIAL PRIMARY KEY,
    zeit_id INT REFERENCES dim_zeit(zeit_id),
    preis_eur_kwh DECIMAL(12,5),
    marktgebiet VARCHAR(100)
);

-- ---------------------------------------------------------
-- FACT: Lieferantenpreis
-- ---------------------------------------------------------
CREATE TABLE fact_lieferantenpreis (
    preis_id SERIAL PRIMARY KEY,
    zeit_id INT REFERENCES dim_zeit(zeit_id),
    lieferant_id INT REFERENCES dim_lieferant(lieferant_id),
    preis_eur_kwh DECIMAL(12,5)
);