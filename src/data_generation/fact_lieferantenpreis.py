import pandas as pd
import numpy as np
from pathlib import Path

# Pfade
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent.parent / "data" / "generated"
INPUT_FILE = DATA_DIR / "fact_spotmarkt.csv"
OUTPUT_DIR = SCRIPT_DIR.parent.parent / "data" / "generated"

# Lieferanten: lieferant_id -> (Code, Name, Aufschlag, Volatilität)
LIEFERANTEN = {
    1: ("VATT", "Vattenfall", 0.16, 0.02),
    2: ("EOND", "E.ON Direkt", 0.15, 0.015),
    3: ("NATU", "Naturstrom", 0.19, 0.01),
    4: ("SPOT", "Spotmarkt-Direkt", 0.12, 0.05),
}


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    # CSV laden
    print(f"Lade: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE, sep=";", decimal=",", low_memory=False)
    print(f"Geladen: {len(df)} Zeilen")

    # Sicherstellen, dass preis_eur_kwh numerisch ist
    df["preis_eur_kwh"] = pd.to_numeric(df["preis_eur_kwh"], errors="coerce")

    # NaN entfernen
    vorher = len(df)
    df = df.dropna(subset=["preis_eur_kwh"])
    print(f"Nach dropna: {len(df)} Zeilen (entfernt: {vorher - len(df)})")

    # Langes Format: Für jede zeit_id und jeden lieferant_id eine Zeile
    rows = []
    preis_id = 1
    np.random.seed(42)

    for _, row in df.iterrows():
        zeit_id = row["zeit_id"]
        spot_preis = row["preis_eur_kwh"]

        for lieferant_id, (code, name, aufschlag, vola) in LIEFERANTEN.items():
            zufall = np.random.uniform(1 - vola, 1 + vola)
            preis_eur_kwh = (spot_preis + aufschlag) * zufall

            rows.append(
                {
                    "preis_id": preis_id,
                    "zeit_id": zeit_id,
                    "lieferant_id": lieferant_id,
                    "preis_eur_kwh": round(preis_eur_kwh, 6),
                }
            )
            preis_id += 1

    df_out = pd.DataFrame(rows)

    print(f"fact_lieferantenpreis.csv erstellt mit {len(df_out)} Zeilen")

    # Speichern
    output_file = OUTPUT_DIR / "fact_lieferantenpreis.csv"
    df_out.to_csv(output_file, sep=";", index=False)


if __name__ == "__main__":
    main()
