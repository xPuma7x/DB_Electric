from src.data_generation.generate_all import main as generate_all
from src.data_loading.load_to_sqlite import main as load_to_sqlite
from src.queries.run_queries import main as run_queries


def main():
    print("Starte Datenbank-Projekt")
    generate_all()
    print("Daten generiert")
    load_to_sqlite()
    print("Daten in SQLite geladen")
    run_queries()
    print("Queries ausgeführt")


if __name__ == "__main__":
    main()
