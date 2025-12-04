import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

SCRIPTS = [
    "dim_lieferant.py",
    "dim_linie.py",
    "dim_standort.py",
    "dim_vertrag.py",
    "dim_zeit_gen.py",
    "fact_energie.py",
    "fact_production.py",
    "fact_spotmarkt.py",
    "fact_lieferantenpreis.py",
]


def main():
    print("=" * 50)
    print("STARTE DATENGENERIERUNG")
    print("=" * 50)

    for script in SCRIPTS:
        script_path = SCRIPT_DIR / script

        if not script_path.exists():
            print(f"\n⚠ SKIP: {script} (nicht gefunden)")
            continue

        print(f"\n>>> {script}")
        print("-" * 40)

        result = subprocess.run(
            [sys.executable, str(script_path)], capture_output=False
        )

        if result.returncode != 0:
            print(f"✗ FEHLER bei {script}")
        else:
            print("✓ OK")

    print("\n" + "=" * 50)
    print("FERTIG")
    print("=" * 50)


if __name__ == "__main__":
    main()
