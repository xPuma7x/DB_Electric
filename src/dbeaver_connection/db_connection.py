from sqlalchemy import create_engine

def get_engine():
    engine = create_engine(
        "postgresql://admin:admin@localhost:5432/energy_db"
    )
    return engine