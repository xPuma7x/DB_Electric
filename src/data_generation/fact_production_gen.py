import pandas as pd
import numpy as np
from pathlib import Path

# Pfade
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent.parent / "data"
OUTPUT_DIR = DATA_DIR / ""

# Standorte und Linien (muss zu dim_standort/dim_linie passen)
STANDORTE = {
    1: {"code": "BER", "name": "Berlin-Adlershof", "effizienz": 1.0},
    2: {"code": "MUC", "name": "München-Garching", "effizienz": 1.0},
    3: {"code": "HAM", "name": "Hamburg-Harburg", "effizienz": 0.80},   # Ineffizient! (Frage 1)
    4: {"code": "FRA", "name": "Frankfurt-Höchst", "effizienz": 1.0},
    5: {"code": "LEI", "name": "Leipzig-Plagwitz", "effizienz": 1.10},  # Sehr effizient
}

LINIEN = {
    1:  {"standort_id": 1, "code": "BER-L1", "typ": "Spritzguss", "basis_menge": 1200},
    2:  {"standort_id": 1, "code": "BER-L2", "typ": "Spritzguss", "basis_menge": 1100},
    3:  {"standort_id": 1, "code": "BER-L3", "typ": "Montage", "basis_menge": 800},
    4:  {"standort_id": 2, "code": "MUC-L1", "typ": "Spritzguss", "basis_menge": 1300},
    5:  {"standort_id": 2, "code": "MUC-L2", "typ": "Spritzguss", "basis_menge": 1250},
    6:  {"standort_id": 2, "code": "MUC-L3", "typ": "Montage", "basis_menge": 850},
    7:  {"standort_id": 3, "code": "HAM-L1", "typ": "Spritzguss", "basis_menge": 1150},
    8:  {"standort_id": 3, "code": "HAM-L2", "typ": "Spritzguss", "basis_menge": 1100},
    9:  {"standort_id": 3, "code": "HAM-L3", "typ": "Montage", "basis_menge": 750},
    10: {"standort_id": 4, "code": "FRA-L1", "typ": "Spritzguss", "basis_menge": 1200},
    11: {"standort_id": 4, "code": "FRA-L2", "typ": "Spritzguss", "basis_menge": 1150},
    12: {"standort_id": 4, "code": "FRA-L3", "typ": "Montage", "basis_menge": 800},
    13: {"standort_id": 5, "code": "LEI-L1", "typ": "Spritzguss", "basis_menge": 1250},
    14: {"standort_id": 5, "code": "LEI-L2", "typ": "Spritzguss", "basis_menge": 1200},
    15: {"standort_id": 5, "code": "LEI-L3", "typ": "Montage", "basis_menge": 820},
}

SCHICHTEN = {
    "Frueh": {"start": 6, "faktor": 1.0},
    "Spaet": {"start": 14, "faktor": 0.95},
    "Nacht": {"start": 22, "faktor": 0.85},
}


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    np.random.seed(42)
    
    print("Generiere fact_produktion...")
    
    # Alle Tage im Zeitraum
    tage = pd.date_range(start="2023-01-01", end="2024-12-31", freq="D")
    
    rows = []
    produktion_id = 1
    
    for tag in tage:
        ist_werktag = tag.dayofweek < 5
        ist_wochenende = not ist_werktag
        
        for linie_id, linie in LINIEN.items():
            standort_id = linie["standort_id"]
            effizienz = STANDORTE[standort_id]["effizienz"]
            basis_menge = linie["basis_menge"]
            
            for schicht_name, schicht in SCHICHTEN.items():
                # Wochenende: 50% Chance auf Stillstand
                if ist_wochenende and np.random.random() < 0.5:
                    continue
                
                # zeit_id: Datum + Schichtbeginn
                stunde = schicht["start"]
                zeit_id = int(tag.strftime("%Y%m%d") + f"{stunde:02d}00")
                
                # Auslastung berechnen
                basis_auslastung = 82  # Durchschnitt
                schicht_faktor = schicht["faktor"]
                wochenend_faktor = 0.7 if ist_wochenende else 1.0
                zufall = np.random.normal(0, 5)  # ±5% Schwankung
                
                auslastung = basis_auslastung * schicht_faktor * wochenend_faktor + zufall
                auslastung = np.clip(auslastung, 40, 98)
                
                # Menge berechnen
                menge_gut = basis_menge * effizienz * (auslastung / 100) * schicht_faktor
                menge_gut = int(menge_gut * np.random.uniform(0.95, 1.05))
                
                # Ausschuss: 2-5%
                ausschuss_rate = np.random.uniform(0.02, 0.05)
                menge_ausschuss = int(menge_gut * ausschuss_rate)
                
                # Laufzeit: 8h Schicht minus Pausen/Störungen
                laufzeit_minuten = int(480 * (auslastung / 100) * np.random.uniform(0.9, 1.0))
                
                rows.append({
                    "produktion_id": produktion_id,
                    "zeit_id": zeit_id,
                    "linie_id": linie_id,
                    "menge_gut": menge_gut,
                    "menge_ausschuss": menge_ausschuss,
                    "auslastung_pct": round(auslastung, 1),
                    "laufzeit_minuten": laufzeit_minuten,
                })
                
                produktion_id += 1
    
    df = pd.DataFrame(rows)
    
    # Speichern
    output_file = OUTPUT_DIR / "fact_produktion.csv"
    df.to_csv(output_file, sep=";", index=False)
    
    print(f"Gespeichert: {output_file}")
    print(f"Zeilen: {len(df):,}")
    
    # Statistiken
    print(f"\nStatistiken:")
    print(f"  Menge gut:    {df['menge_gut'].mean():,.0f} Ø pro Schicht")
    print(f"  Ausschuss:    {df['menge_ausschuss'].mean():,.0f} Ø pro Schicht")
    print(f"  Auslastung:   {df['auslastung_pct'].mean():.1f}% Ø")
    print(f"  Laufzeit:     {df['laufzeit_minuten'].mean():.0f} min Ø")
    
    # Pro Standort (für Frage 1: Ausreißer prüfen)
    print(f"\nMenge pro Standort:")
    df_mit_standort = df.copy()
    df_mit_standort["standort_id"] = df_mit_standort["linie_id"].apply(
        lambda x: LINIEN[x]["standort_id"]
    )
    df_mit_standort["standort"] = df_mit_standort["standort_id"].apply(
        lambda x: STANDORTE[x]["code"]
    )
    print(df_mit_standort.groupby("standort")["menge_gut"].mean().round(0))


if __name__ == "__main__":
    main()