import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "generated"

LIEFERANTEN = [
    {
        "lieferant_id": 1,
        "lieferant_code": "VATT",
        "lieferant_name": "Vattenfall",
        "typ": "Mix",
    },
    {
        "lieferant_id": 2,
        "lieferant_code": "EOND",
        "lieferant_name": "E.ON Direkt",
        "typ": "Mix",
    },
    {
        "lieferant_id": 3,
        "lieferant_code": "NATU",
        "lieferant_name": "Naturstrom",
        "typ": "Öko",
    },
    {
        "lieferant_id": 4,
        "lieferant_code": "SPOT",
        "lieferant_name": "Spotmarkt-Direkt",
        "typ": "Spot",
    },
]


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    df = pd.DataFrame(LIEFERANTEN)

    output_file = OUTPUT_DIR / "dim_lieferant.csv"
    df.to_csv(output_file, sep=";", index=False)

    print(f"dim_lieferant.csv erstellt mit {len(df)} Zeilen")


if __name__ == "__main__":
    main()
