import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "generated"

STANDORTE = [
    {
        "standort_id": 1,
        "standort_code": "BER",
        "standort_name": "Berlin-Adlershof",
        "land": "DE",
        "region": "Ost",
    },
    {
        "standort_id": 2,
        "standort_code": "MUC",
        "standort_name": "München-Garching",
        "land": "DE",
        "region": "Süd",
    },
    {
        "standort_id": 3,
        "standort_code": "HAM",
        "standort_name": "Hamburg-Harburg",
        "land": "DE",
        "region": "Nord",
    },
    {
        "standort_id": 4,
        "standort_code": "FRA",
        "standort_name": "Frankfurt-Höchst",
        "land": "DE",
        "region": "West",
    },
    {
        "standort_id": 5,
        "standort_code": "LEI",
        "standort_name": "Leipzig-Plagwitz",
        "land": "DE",
        "region": "Ost",
    },
]


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    df = pd.DataFrame(STANDORTE)

    output_file = OUTPUT_DIR / "dim_standort.csv"
    df.to_csv(output_file, sep=";", index=False)

    print(f"dim_standort.csv erstellt mit {len(df)} Zeilen")


if __name__ == "__main__":
    main()
