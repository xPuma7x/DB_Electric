#!/usr/bin/env python3
"""SQL Benchmark für DB_Electric."""

import argparse
import json
import sqlite3
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DB_FILE = PROJECT_DIR / "data" / "stromkosten.db"
OUTPUT_DIR = PROJECT_DIR / "output" / "benchmarks"

QUERIES = [
    ("Frage1", "src/queries/frage1.sql", "Stromkosten (Naive)"),
    ("Frage2", "src/queries/frage2.sql", "Lastspitzen (Naive)"),
    ("Frage2_Opt", "src/queries/frage2_optimized.sql", "Lastspitzen (Index)"),
    ("Frage3", "src/queries/frage3.sql", "Lieferanten (UNION)"),
    ("Frage3_Opt", "src/queries/frage3_optimized.sql", "Lieferanten (CTE)"),
]


def reset_database():
    """Datenbank neu erstellen."""
    print("\n[RESET] Datenbank wird neu erstellt...")
    loader = SCRIPT_DIR / "data_loading" / "load_to_sqlite.py"
    subprocess.run([sys.executable, str(loader)], check=True, cwd=PROJECT_DIR)
    print("   Daten geladen")


def setup_indexes(db_path: Path):
    """Benchmark-Indizes erstellen."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_energie_leistung 
        ON fact_energie(leistung_max_kw) 
        WHERE leistung_max_kw > 500
    """)
    conn.close()


def drop_indexes(db_path: Path):
    """Benchmark-Indizes entfernen."""
    conn = sqlite3.connect(db_path)
    conn.execute("DROP INDEX IF EXISTS idx_energie_leistung")
    conn.close()


def run_query(db_path: Path, query_file: Path, iterations: int) -> dict:
    """Query mehrfach ausführen und Zeiten messen."""
    times = []
    sql = query_file.read_text(encoding="utf-8")

    for _ in range(iterations):
        conn = sqlite3.connect(db_path)
        start = time.perf_counter()
        conn.execute(sql).fetchall()
        elapsed = time.perf_counter() - start
        conn.close()
        times.append(elapsed)

    return {
        "times": times,
        "min": min(times),
        "max": max(times),
        "avg": sum(times) / len(times),
    }


def main():
    parser = argparse.ArgumentParser(description="SQL Benchmark für DB_Electric")
    parser.add_argument("-i", "--iterations", type=int, default=3, help="Anzahl Iterationen")
    parser.add_argument("-r", "--reset", action="store_true", help="Datenbank neu erstellen")
    parser.add_argument("-v", "--verbose", action="store_true", help="Detaillierte Ausgabe")
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 54)
    print("         SQL BENCHMARK - DB_Electric")
    print("=" * 54)
    print(f"  Datenbank:   {DB_FILE}")
    print(f"  Iterationen: {args.iterations}")
    print(f"  Reset:       {args.reset}")
    print(f"  Zeitstempel: {timestamp}\n")

    if args.reset:
        reset_database()

    if not DB_FILE.exists():
        print(f"FEHLER: Datenbank '{DB_FILE}' nicht gefunden!")
        return 1

    # Indizes entfernen für fairen Vergleich
    drop_indexes(DB_FILE)

    print("-" * 54)

    results = []
    for name, file, description in QUERIES:
        # Index NUR für optimierte Frage2 erstellen
        if name == "Frage2_Opt":
            print("\n[INDEX] Erstelle idx_energie_leistung...")
            setup_indexes(DB_FILE)

        query_file = PROJECT_DIR / file
        print(f"\n>> {description}")
        print(f"   Datei: {file}")

        if not query_file.exists():
            print("   UEBERSPRUNGEN: Datei nicht gefunden")
            continue

        benchmark = run_query(DB_FILE, query_file, args.iterations)

        result = {
            "name": name,
            "description": description,
            "file": file,
            "min_time": round(benchmark["min"], 6),
            "max_time": round(benchmark["max"], 6),
            "avg_time": round(benchmark["avg"], 6),
            "iterations": args.iterations,
            "timestamp": timestamp,
        }
        results.append(result)

        avg_ms = benchmark["avg"] * 1000
        print(f"   Min: {benchmark['min']:.6f}s")
        print(f"   Max: {benchmark['max']:.6f}s")
        print(f"   Avg: \033[92m{avg_ms:.2f} ms\033[0m")

    # Zusammenfassung
    print("\n" + "-" * 54)
    print("\n[ZUSAMMENFASSUNG]\n")
    print(f"{'Query':<20} {'Avg (ms)':>12} {'Min (ms)':>12} {'Speedup':>10}")
    print("-" * 56)

    def get_result(name):
        return next((r for r in results if r["name"] == name), None)

    frage1 = get_result("Frage1")
    frage2 = get_result("Frage2")
    frage3 = get_result("Frage3")

    for r in results:
        avg_ms = r["avg_time"] * 1000
        min_ms = r["min_time"] * 1000
        speedup = "-"

        if r["name"] == "Frage1_Opt" and frage1 and r["avg_time"] > 0:
            speedup = f"{frage1['avg_time'] / r['avg_time']:.1f}x"
        elif r["name"] == "Frage2_Opt" and frage2 and r["avg_time"] > 0:
            speedup = f"{frage2['avg_time'] / r['avg_time']:.1f}x"
        elif r["name"] == "Frage3_Opt" and frage3 and r["avg_time"] > 0:
            speedup = f"{frage3['avg_time'] / r['avg_time']:.1f}x"

        print(f"{r['description']:<20} {avg_ms:>12.2f} {min_ms:>12.2f} {speedup:>10}")

    # Speichern
    json_file = OUTPUT_DIR / f"benchmark_{timestamp}.json"
    json_file.write_text(json.dumps(results, indent=2))

    csv_file = OUTPUT_DIR / f"benchmark_{timestamp}.csv"
    csv_lines = ["Name,Description,File,MinTime,MaxTime,AvgTime,Iterations,Timestamp"]
    for r in results:
        csv_lines.append(f"{r['name']},{r['description']},{r['file']},{r['min_time']},{r['max_time']},{r['avg_time']},{r['iterations']},{r['timestamp']}")
    csv_file.write_text("\n".join(csv_lines))

    print("\n" + "-" * 54)
    print("\n[GESPEICHERT]")
    print(f"   JSON: {json_file}")
    print(f"   CSV:  {csv_file}")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
