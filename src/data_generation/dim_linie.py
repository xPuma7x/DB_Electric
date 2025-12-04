import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "generated"

LINIEN = [
    # Berlin (standort_id=1)
    {
        "linie_id": 1,
        "standort_id": 1,
        "linie_code": "BER-L1",
        "linie_name": "Spritzguss 1",
        "technologie": "Spritzguss",
        "nennleistung_kw": 450,
    },
    {
        "linie_id": 2,
        "standort_id": 1,
        "linie_code": "BER-L2",
        "linie_name": "Spritzguss 2",
        "technologie": "Spritzguss",
        "nennleistung_kw": 520,
    },
    {
        "linie_id": 3,
        "standort_id": 1,
        "linie_code": "BER-L3",
        "linie_name": "Montage 1",
        "technologie": "Montage",
        "nennleistung_kw": 180,
    },
    # München (standort_id=2)
    {
        "linie_id": 4,
        "standort_id": 2,
        "linie_code": "MUC-L1",
        "linie_name": "Spritzguss 1",
        "technologie": "Spritzguss",
        "nennleistung_kw": 480,
    },
    {
        "linie_id": 5,
        "standort_id": 2,
        "linie_code": "MUC-L2",
        "linie_name": "Spritzguss 2",
        "technologie": "Spritzguss",
        "nennleistung_kw": 550,
    },
    {
        "linie_id": 6,
        "standort_id": 2,
        "linie_code": "MUC-L3",
        "linie_name": "Montage 1",
        "technologie": "Montage",
        "nennleistung_kw": 200,
    },
    # Hamburg (standort_id=3)
    {
        "linie_id": 7,
        "standort_id": 3,
        "linie_code": "HAM-L1",
        "linie_name": "Spritzguss 1",
        "technologie": "Spritzguss",
        "nennleistung_kw": 460,
    },
    {
        "linie_id": 8,
        "standort_id": 3,
        "linie_code": "HAM-L2",
        "linie_name": "Spritzguss 2",
        "technologie": "Spritzguss",
        "nennleistung_kw": 490,
    },
    {
        "linie_id": 9,
        "standort_id": 3,
        "linie_code": "HAM-L3",
        "linie_name": "Montage 1",
        "technologie": "Montage",
        "nennleistung_kw": 170,
    },
    # Frankfurt (standort_id=4)
    {
        "linie_id": 10,
        "standort_id": 4,
        "linie_code": "FRA-L1",
        "linie_name": "Spritzguss 1",
        "technologie": "Spritzguss",
        "nennleistung_kw": 440,
    },
    {
        "linie_id": 11,
        "standort_id": 4,
        "linie_code": "FRA-L2",
        "linie_name": "Spritzguss 2",
        "technologie": "Spritzguss",
        "nennleistung_kw": 470,
    },
    {
        "linie_id": 12,
        "standort_id": 4,
        "linie_code": "FRA-L3",
        "linie_name": "Montage 1",
        "technologie": "Montage",
        "nennleistung_kw": 190,
    },
    # Leipzig (standort_id=5)
    {
        "linie_id": 13,
        "standort_id": 5,
        "linie_code": "LEI-L1",
        "linie_name": "Spritzguss 1",
        "technologie": "Spritzguss",
        "nennleistung_kw": 450,
    },
    {
        "linie_id": 14,
        "standort_id": 5,
        "linie_code": "LEI-L2",
        "linie_name": "Spritzguss 2",
        "technologie": "Spritzguss",
        "nennleistung_kw": 480,
    },
    {
        "linie_id": 15,
        "standort_id": 5,
        "linie_code": "LEI-L3",
        "linie_name": "Montage 1",
        "technologie": "Montage",
        "nennleistung_kw": 185,
    },
]


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    df = pd.DataFrame(LINIEN)

    output_file = OUTPUT_DIR / "dim_linie.csv"
    df.to_csv(output_file, sep=";", index=False)

    print(f"Gespeichert: {output_file}")
    print(f"Zeilen: {len(df)}")
    print(df)


if __name__ == "__main__":
    main()
