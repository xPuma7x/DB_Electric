import sqlite3
import pandas as pd
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent.parent / "data" / "generated"
DB_FILE = SCRIPT_DIR.parent.parent / "data" / "stromkosten.db"
DDL_FILE = SCRIPT_DIR.parent.parent / "data" / "create_tables.sql"

# CSV → Tabelle Mapping
IMPORTS = [
    ("dim_zeit.csv", "dim_zeit"),
    ("dim_standort.csv", "dim_standort"),
    ("dim_linie.csv", "dim_linie"),
    ("dim_lieferant.csv", "dim_lieferant"),
    ("dim_vertrag.csv", "dim_vertrag"),
    ("fact_produktion.csv", "fact_produktion"),
    ("fact_energie.csv", "fact_energie"),
    ("fact_spotmarkt.csv", "fact_spotmarkt"),
    ("fact_lieferantenpreis.csv", "fact_lieferantenpreis"),
]


def main():
    # Alte DB löschen
    if DB_FILE.exists():
        DB_FILE.unlink()
        print(f"Alte DB gelöscht: {DB_FILE}")

    # Verbinden
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # DDL ausführen
    print("\nErstelle Tabellen...")
    with open(DDL_FILE, "r") as f:
        cursor.executescript(f.read())
    print("✓ Tabellen erstellt")

    # CSVs importieren
    print("\nImportiere Daten...")
    for csv_file, table_name in IMPORTS:
        csv_path = DATA_DIR / csv_file

        if not csv_path.exists():
            print(f"⚠ SKIP: {csv_file} (nicht gefunden)")
            continue

        df = pd.read_csv(csv_path, sep=";")
        df.to_sql(table_name, conn, if_exists="append", index=False)
        print(f"✓ {table_name}: {len(df):,} Zeilen")

    conn.commit()

    # Prüfen
    print("\nTabellen in DB:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for row in cursor.fetchall():
        cursor.execute(f"SELECT COUNT(*) FROM {row[0]}")
        count = cursor.fetchone()[0]
        print(f"  {row[0]}: {count:,}")

    conn.close()
    print(f"\n✓ Fertig: {DB_FILE}")


if __name__ == "__main__":
    main()
