import sqlite3
import pandas as pd
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DB_FILE = SCRIPT_DIR.parent.parent / "data" / "stromkosten.db"


def run_query(sql_file: str):
    """Führt SQL-Datei aus und zeigt Ergebnis."""
    sql_path = SCRIPT_DIR / sql_file

    with open(sql_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # SQLite CLI-Befehle (z.B. .timer, .scanstats) filtern
    query = "".join(line for line in lines if not line.strip().startswith("."))

    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql(query, conn)
    conn.close()

    return df


def main():
    print("=" * 60)
    print("FRAGE 1: Stromkostenintensität")
    print("=" * 60)

    df = run_query("frage1.sql")

    if df.empty:
        print("Keine Standorte > 15% über Durchschnitt")
    else:
        print(df.to_string(index=False))

    print()

    #########################################################
    print("=" * 60)
    print("FRAGE 2: Lastspitzen-Analyse")
    print("=" * 60)

    df = run_query("frage2.sql")
    if df.empty:
        print("Keine Lastspitzen gefunden")
    else:
        print(df.to_string(index=False))

    print()

    #########################################################
    print("=" * 60)
    print("FRAGE 3: Lieferantenpreis-Analyse")
    print("=" * 60)

    df = run_query("frage3.sql")
    if df.empty:
        print("Keine Daten gefunden")
    else:
        print(df.to_string(index=False))

    print()


if __name__ == "__main__":
    main()
