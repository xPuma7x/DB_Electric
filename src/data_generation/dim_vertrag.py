import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "generated"

# n:m Beziehung: Welcher Standort hat wann welchen Lieferanten?
VERTRAEGE = [
    # Berlin: Wechsel von Vattenfall zu E.ON Mitte 2024
    {
        "vertrag_id": 1,
        "lieferant_id": 1,
        "standort_id": 1,
        "vertragsnummer": "V-2023-001",
        "gueltig_ab": "2023-01-01",
        "gueltig_bis": "2024-06-30",
        "grundpreis_eur_monat": 450,
    },
    {
        "vertrag_id": 2,
        "lieferant_id": 2,
        "standort_id": 1,
        "vertragsnummer": "V-2024-001",
        "gueltig_ab": "2024-07-01",
        "gueltig_bis": "2024-12-31",
        "grundpreis_eur_monat": 480,
    },
    # München: Vattenfall durchgehend
    {
        "vertrag_id": 3,
        "lieferant_id": 1,
        "standort_id": 2,
        "vertragsnummer": "V-2023-002",
        "gueltig_ab": "2023-01-01",
        "gueltig_bis": "2024-12-31",
        "grundpreis_eur_monat": 520,
    },
    # Hamburg: Naturstrom (Öko, teuer)
    {
        "vertrag_id": 4,
        "lieferant_id": 3,
        "standort_id": 3,
        "vertragsnummer": "V-2023-003",
        "gueltig_ab": "2023-01-01",
        "gueltig_bis": "2024-12-31",
        "grundpreis_eur_monat": 380,
    },
    # Frankfurt: E.ON durchgehend
    {
        "vertrag_id": 5,
        "lieferant_id": 2,
        "standort_id": 4,
        "vertragsnummer": "V-2023-004",
        "gueltig_ab": "2023-01-01",
        "gueltig_bis": "2024-12-31",
        "grundpreis_eur_monat": 460,
    },
    # Leipzig: Spotmarkt-Direkt (günstig, volatil)
    {
        "vertrag_id": 6,
        "lieferant_id": 4,
        "standort_id": 5,
        "vertragsnummer": "V-2023-005",
        "gueltig_ab": "2023-01-01",
        "gueltig_bis": "2024-12-31",
        "grundpreis_eur_monat": 350,
    },
]


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    df = pd.DataFrame(VERTRAEGE)

    output_file = OUTPUT_DIR / "dim_vertrag.csv"
    df.to_csv(output_file, sep=";", index=False)

    print(f"Gespeichert: {output_file}")
    print(f"Zeilen: {len(df)}")
    print(df)


if __name__ == "__main__":
    main()
