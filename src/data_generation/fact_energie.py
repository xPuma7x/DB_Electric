import pandas as pd
import numpy as np
from pathlib import Path

# Pfade
SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR.parent.parent / "data" / "generated"

# Linien mit Energieprofilen
LINIEN = {
    1: {
        "standort_id": 1,
        "code": "BER-L1",
        "typ": "Spritzguss",
        "nennleistung_kw": 450,
    },
    2: {
        "standort_id": 1,
        "code": "BER-L2",
        "typ": "Spritzguss",
        "nennleistung_kw": 520,
    },
    3: {"standort_id": 1, "code": "BER-L3", "typ": "Montage", "nennleistung_kw": 180},
    4: {
        "standort_id": 2,
        "code": "MUC-L1",
        "typ": "Spritzguss",
        "nennleistung_kw": 480,
    },
    5: {
        "standort_id": 2,
        "code": "MUC-L2",
        "typ": "Spritzguss",
        "nennleistung_kw": 550,
    },
    6: {"standort_id": 2, "code": "MUC-L3", "typ": "Montage", "nennleistung_kw": 200},
    7: {
        "standort_id": 3,
        "code": "HAM-L1",
        "typ": "Spritzguss",
        "nennleistung_kw": 460,
    },
    8: {
        "standort_id": 3,
        "code": "HAM-L2",
        "typ": "Spritzguss",
        "nennleistung_kw": 490,
    },
    9: {"standort_id": 3, "code": "HAM-L3", "typ": "Montage", "nennleistung_kw": 170},
    10: {
        "standort_id": 4,
        "code": "FRA-L1",
        "typ": "Spritzguss",
        "nennleistung_kw": 440,
    },
    11: {
        "standort_id": 4,
        "code": "FRA-L2",
        "typ": "Spritzguss",
        "nennleistung_kw": 470,
    },
    12: {"standort_id": 4, "code": "FRA-L3", "typ": "Montage", "nennleistung_kw": 190},
    13: {
        "standort_id": 5,
        "code": "LEI-L1",
        "typ": "Spritzguss",
        "nennleistung_kw": 450,
    },
    14: {
        "standort_id": 5,
        "code": "LEI-L2",
        "typ": "Spritzguss",
        "nennleistung_kw": 480,
    },
    15: {"standort_id": 5, "code": "LEI-L3", "typ": "Montage", "nennleistung_kw": 185},
}

# Verträge: Welcher Standort hat wann welchen Vertrag?
VERTRAEGE = {
    1: {
        "standort_id": 1,
        "lieferant": "VATT",
        "von": "2023-01-01",
        "bis": "2024-06-30",
    },
    2: {
        "standort_id": 1,
        "lieferant": "EOND",
        "von": "2024-07-01",
        "bis": "2024-12-31",
    },
    3: {
        "standort_id": 2,
        "lieferant": "VATT",
        "von": "2023-01-01",
        "bis": "2024-12-31",
    },
    4: {
        "standort_id": 3,
        "lieferant": "NATU",
        "von": "2023-01-01",
        "bis": "2024-12-31",
    },
    5: {
        "standort_id": 4,
        "lieferant": "EOND",
        "von": "2023-01-01",
        "bis": "2024-12-31",
    },
    6: {
        "standort_id": 5,
        "lieferant": "SPOT",
        "von": "2023-01-01",
        "bis": "2024-12-31",
    },
}

# Standort-Faktoren (für Anomalien)
STANDORT_FAKTOREN = {
    1: {"verbrauch": 1.0, "spitzen_rate": 0.03},  # Berlin: Normal
    2: {"verbrauch": 1.0, "spitzen_rate": 0.08},  # München: Viele Spitzen! (Frage 2)
    3: {"verbrauch": 1.15, "spitzen_rate": 0.03},  # Hamburg: Hoher Verbrauch (Frage 1)
    4: {"verbrauch": 1.0, "spitzen_rate": 0.03},  # Frankfurt: Normal
    5: {"verbrauch": 0.90, "spitzen_rate": 0.02},  # Leipzig: Effizient
}

# Schicht-Faktoren
SCHICHT_FAKTOREN = {
    "Frueh": 1.0,
    "Spaet": 1.15,  # Höhere Last in Spätschicht
    "Nacht": 0.75,
}


def get_schicht(stunde: int) -> str:
    if stunde >= 22 or stunde < 6:
        return "Nacht"
    elif stunde >= 6 and stunde < 14:
        return "Frueh"
    else:
        return "Spaet"


def get_vertrag_id(standort_id: int, datum: pd.Timestamp) -> int:
    """Findet den gültigen Vertrag für Standort und Datum."""
    for vertrag_id, v in VERTRAEGE.items():
        if v["standort_id"] == standort_id:
            von = pd.Timestamp(v["von"])
            bis = pd.Timestamp(v["bis"])
            if von <= datum <= bis:
                return vertrag_id
    return None


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    np.random.seed(42)

    print("Generiere fact_energie...")
    print("Das kann etwas dauern (~500k Zeilen)...")

    # Alle 15-Min-Intervalle
    timestamps = pd.date_range(
        start="2023-01-01 00:00", end="2024-12-31 23:45", freq="15min"
    )

    rows = []
    energie_id = 1

    total = len(timestamps) * len(LINIEN)
    checkpoint = total // 10

    for i, ts in enumerate(timestamps):
        ist_werktag = ts.dayofweek < 5
        stunde = ts.hour
        schicht = get_schicht(stunde)
        schicht_faktor = SCHICHT_FAKTOREN[schicht]
        zeit_id = int(ts.strftime("%Y%m%d%H%M"))

        for linie_id, linie in LINIEN.items():
            standort_id = linie["standort_id"]
            standort_f = STANDORT_FAKTOREN[standort_id]
            nennleistung = linie["nennleistung_kw"]

            # Vertrag für diesen Standort/Zeitpunkt
            vertrag_id = get_vertrag_id(standort_id, ts)

            # Wochenende: Reduzierter Betrieb oder Stillstand
            if not ist_werktag:
                if np.random.random() < 0.3:  # 30% Stillstand
                    continue
                betrieb_faktor = 0.5
            else:
                betrieb_faktor = 1.0

            # Basisleistung: 60-85% der Nennleistung
            basis_leistung = nennleistung * np.random.uniform(0.60, 0.85)

            # Faktoren anwenden
            leistung = (
                basis_leistung
                * schicht_faktor
                * betrieb_faktor
                * standort_f["verbrauch"]
            )

            # Zufällige Schwankung
            leistung *= np.random.uniform(0.9, 1.1)

            # Lastspitzen (für Frage 2)
            if np.random.random() < standort_f["spitzen_rate"]:
                # Spitze: 100-130% der Nennleistung
                leistung = nennleistung * np.random.uniform(1.0, 1.3)

            leistung_max_kw = round(leistung, 2)

            # Verbrauch in kWh (Leistung × 0.25h)
            verbrauch_kwh = round(leistung_max_kw * 0.25, 4)

            # Messstatus: 95% OK, 3% FEHLER, 2% NULL
            rand = np.random.random()
            if rand < 0.02:
                messstatus = "NULL"
                verbrauch_kwh = None
                leistung_max_kw = None
            elif rand < 0.05:
                messstatus = "FEHLER"
            else:
                messstatus = "OK"

            rows.append(
                {
                    "energie_id": energie_id,
                    "zeit_id": zeit_id,
                    "linie_id": linie_id,
                    "vertrag_id": vertrag_id,
                    "verbrauch_kwh": verbrauch_kwh,
                    "leistung_max_kw": leistung_max_kw,
                    "messstatus": messstatus,
                }
            )

            energie_id += 1

        # Fortschritt
        if (i * len(LINIEN)) % checkpoint == 0:
            pct = (i * len(LINIEN)) / total * 100
            print(f"  {pct:.0f}% ...")

    df = pd.DataFrame(rows)

    # Speichern
    output_file = OUTPUT_DIR / "fact_energie.csv"
    df.to_csv(output_file, sep=";", index=False)

    print(f"fact_energie.csv erstellt mit {len(df)} Zeilen")


if __name__ == "__main__":
    main()
