from src.data_generation.generate_all import main as generate_all
from src.data_loading.load_to_sqlite import main as load_to_sqlite
from src.queries.run_queries import main as run_queries


def main():
    print("Hello from db-electric!")
    generate_all()
    load_to_sqlite()
    run_queries()


if __name__ == "__main__":
    main()
