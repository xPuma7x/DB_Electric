import pandas as pd
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent.parent / "data"
OUTPUT_DIR = DATA_DIR / "generated"


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    # CSV laden
    print("Lade SMARD-Daten...")
    df = pd.read_csv(
        DATA_DIR / "grosshandelpreise_2022_2025_15min.csv",
        sep=";",
        decimal=",",
        low_memory=False,
    )

    # Nur relevante Spalten
    df = df[["Datum von", "Deutschland/Luxemburg [€/MWh] Originalauflösungen"]].copy()

    # Umbenennen
    df.columns = ["datum_von", "preis_eur_mwh"]

    # NaN entfernen
    df = df.dropna()

    # Zeitraum filtern (2023-2024)
    df["datum_von"] = pd.to_datetime(df["datum_von"], format="%d.%m.%Y %H:%M")
    df = df[(df["datum_von"] >= "2023-01-01") & (df["datum_von"] <= "2024-12-31 23:59")]

    # Spalten für fact_spotmarkt
    df["spot_id"] = range(1, len(df) + 1)
    df["zeit_id"] = df["datum_von"].dt.strftime("%Y%m%d%H%M").astype(int)
    df["preis_eur_kwh"] = pd.to_numeric(df["preis_eur_mwh"], errors="coerce") / 1000
    df["marktgebiet"] = "DE-LU"

    # Finale Spalten
    df = df[["spot_id", "zeit_id", "preis_eur_kwh", "marktgebiet"]]

    # Speichern
    output_file = OUTPUT_DIR / "fact_spotmarkt.csv"
    df.to_csv(output_file, sep=";", index=False)

    print(f"Gespeichert: {output_file}")
    print(f"Zeilen: {len(df):,}")
    print(f"Zeitraum: {df['zeit_id'].min()} - {df['zeit_id'].max()}")
    print(
        f"Preis: {df['preis_eur_kwh'].min():.4f} - {df['preis_eur_kwh'].max():.4f} €/kWh"
    )


if __name__ == "__main__":
    main()
