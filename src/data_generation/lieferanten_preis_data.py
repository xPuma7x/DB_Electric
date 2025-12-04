import pandas as pd
import numpy as np
from pathlib import Path

# Pfade
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent.parent / "data"
INPUT_FILE = DATA_DIR / "smard_spotpreise.csv"
OUTPUT_DIR = DATA_DIR / ""

# Lieferanten: Code -> (Name, Aufschlag, Volatilität)
LIEFERANTEN = {
    "VATT": ("Vattenfall", 0.16, 0.02),
    "EOND": ("E.ON Direkt", 0.15, 0.015),
    "NATU": ("Naturstrom", 0.19, 0.01),
    "SPOT": ("Spotmarkt-Direkt", 0.12, 0.05),
}


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # CSV laden
    print(f"Lade: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE, sep=';', decimal=',', low_memory=False)
    print(f"Geladen: {len(df)} Zeilen")
    
    # Nur relevante Spalten behalten
    preis_col = 'Deutschland/Luxemburg [€/MWh] Originalauflösungen'
    df_out = pd.DataFrame()
    df_out['datum_von'] = df['Datum von']
    df_out['datum_bis'] = df['Datum bis']
    df_out['spot_eur_kwh'] = pd.to_numeric(df[preis_col], errors='coerce') / 1000
    
    # NaN entfernen
    vorher = len(df_out)
    df_out = df_out.dropna(subset=['spot_eur_kwh'])
    print(f"Nach dropna: {len(df_out)} Zeilen (entfernt: {vorher - len(df_out)})")
    
    # Debug: Erste Zeilen
    print(f"\nErste 3 Zeilen:")
    print(df_out.head(3))
    
    # Lieferantenpreise generieren
    np.random.seed(42)
    for code, (name, aufschlag, vola) in LIEFERANTEN.items():
        zufall = np.random.uniform(1 - vola, 1 + vola, len(df_out))
        df_out[f'preis_{code}'] = (df_out['spot_eur_kwh'] + aufschlag) * zufall
        print(f"{name}: Ø {df_out[f'preis_{code}'].mean():.4f} €/kWh")
    
    # Debug vor Speichern
    print(f"\nDataFrame vor Speichern:")
    print(f"  Shape: {df_out.shape}")
    print(f"  Spalten: {list(df_out.columns)}")
    
    # Speichern - OHNE decimal Parameter
    output_file = OUTPUT_DIR / "lieferanten_preise.csv"
    df_out.to_csv(output_file, sep=';', index=False)
    
    # Prüfen ob Datei existiert und Größe
    if output_file.exists():
        size = output_file.stat().st_size
        print(f"\nDatei erstellt: {output_file}")
        print(f"Dateigroesse: {size:,} Bytes")
        
        # Erste Zeilen der Datei lesen
        with open(output_file, 'r', encoding='utf-8') as f:
            print(f"\nErste 3 Zeilen der CSV:")
            for i, line in enumerate(f):
                if i < 3:
                    print(f"  {line.strip()}")
    else:
        print(f"\nFEHLER: Datei wurde nicht erstellt!")


if __name__ == "__main__":
    main()