import pandas as pd
from pathlib import Path

# Pfade
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent.parent / "data"
OUTPUT_DIR = DATA_DIR / ""


def get_schicht(stunde: int) -> str:
    """Bestimmt Schicht basierend auf Stunde."""
    if stunde >= 22 or stunde < 6:
        return "Nacht"
    elif stunde >= 6 and stunde < 14:
        return "Frueh"
    else:
        return "Spaet"


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Zeitraum: 01.01.2023 – 31.12.2024, 15-Minuten-Intervalle
    print("Generiere dim_zeit...")
    
    timestamps = pd.date_range(
        start="2023-01-01 00:00",
        end="2024-12-31 23:45",
        freq="15min"
    )
    
    df = pd.DataFrame({"timestamp": timestamps})
    
    # Felder ableiten
    df["zeit_id"] = df["timestamp"].dt.strftime("%Y%m%d%H%M").astype(int)
    df["datum"] = df["timestamp"].dt.date
    df["jahr"] = df["timestamp"].dt.year
    df["quartal"] = df["timestamp"].dt.quarter
    df["monat"] = df["timestamp"].dt.month
    df["kw"] = df["timestamp"].dt.isocalendar().week.astype(int)
    df["tag_im_monat"] = df["timestamp"].dt.day
    df["stunde"] = df["timestamp"].dt.hour
    df["intervall_15min"] = df["stunde"] * 4 + df["timestamp"].dt.minute // 15
    df["schicht"] = df["stunde"].apply(get_schicht)
    df["ist_werktag"] = df["timestamp"].dt.dayofweek < 5  # Mo=0, Fr=4
    
    # Nur finale Spalten behalten
    df = df[[
        "zeit_id", "datum", "jahr", "quartal", "monat", "kw",
        "tag_im_monat", "stunde", "intervall_15min", "schicht", "ist_werktag"
    ]]
    
    # Speichern
    output_file = OUTPUT_DIR / "dim_zeit.csv"
    df.to_csv(output_file, sep=";", index=False)
    
    print(f"Gespeichert: {output_file}")
    print(f"Zeilen: {len(df):,}")
    print(f"\nErste 5 Zeilen:")
    print(df.head())
    print(f"\nLetzte 5 Zeilen:")
    print(df.tail())


if __name__ == "__main__":
    main()