import pandas as pd
from db_connection import get_engine
from pathlib import Path

def import_all_csvs(data_folder: str):
    engine = get_engine()

    folder = Path(data_folder)

    IGNORE_FILES = {
    "grosshandelpreise_2022_2025_15min.csv"
}

    for csv in folder.glob("*.csv"):
        if csv.name in IGNORE_FILES:
            print(f"Ignoriere Datei: {csv.name}")
            continue
        table_name = csv.stem.lower()  # Dateiname = Tabellenname
        print(f"Lade Datei {csv.name} in Tabelle '{table_name}' ...")

        df = pd.read_csv(csv, sep=";")

        df.to_sql(
            table_name,
            engine,
            if_exists="append",  # oder "replace"
            index=False
        )

        print(f"✔ Import abgeschlossen: {table_name}")

if __name__ == "__main__":
    import_all_csvs("../../data")
