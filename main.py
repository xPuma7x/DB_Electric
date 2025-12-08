import argparse

from src.data_generation.generate_all import main as generate_all
from src.data_loading.load_to_sqlite import main as load_to_sqlite
from src.queries.run_queries import main as run_queries
from src.queries.visualize import main as visualize


def main():
    parser = argparse.ArgumentParser(description="Stromkosten-Analyse Pipeline")
    parser.add_argument("--skip-generate", action="store_true", help="Datengenerierung überspringen")
    parser.add_argument("--skip-load", action="store_true", help="Laden in SQLite überspringen")
    parser.add_argument("--visualize", action="store_true", help="Charts erstellen")
    args = parser.parse_args()

    print("=" * 60)
    print("STROMKOSTEN-ANALYSE: Pipeline Start")
    print("=" * 60)

    if not args.skip_generate:
        print("\n[1/3] Generiere Daten...")
        generate_all()
    else:
        print("\n[1/3] Generierung übersprungen (--skip-generate)")

    if not args.skip_load:
        print("\n[2/3] Lade Daten in SQLite...")
        load_to_sqlite()
    else:
        print("\n[2/3] Laden übersprungen (--skip-load)")

    print("\n[3/3] Führe Analyse-Queries aus...")
    run_queries()

    if args.visualize:
        print("\n[4/4] Erstelle Visualisierungen...")
        visualize()

    print("\n" + "=" * 60)
    print("Pipeline abgeschlossen.")
    print("=" * 60)


if __name__ == "__main__":
    main()
