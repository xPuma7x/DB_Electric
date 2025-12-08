"""
Visualisierung der Stromkosten-Analyse
Erstellt Charts für die drei Kernfragen.
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DB_FILE = SCRIPT_DIR.parent.parent / "data" / "stromkosten.db"
OUTPUT_DIR = SCRIPT_DIR.parent.parent / "output"


def run_query(sql_file: str) -> pd.DataFrame:
    """Führt SQL-Datei aus und gibt DataFrame zurück."""
    sql_path = SCRIPT_DIR / sql_file
    with open(sql_path, "r", encoding="utf-8") as f:
        query = f.read()
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def plot_frage1():
    """
    Frage 1: Stromkostenintensität
    Welche Standorte haben Stückkosten >15% über Durchschnitt?
    """
    df = run_query("frage1.sql")

    # Stückkosten berechnen
    df["kosten_pro_stueck"] = (df["verbrauch_kwh"] * df["avg_preis_eur_kwh"]) / df[
        "menge_stueck"
    ]
    durchschnitt = df["kosten_pro_stueck"].mean()
    df["abweichung_pct"] = (df["kosten_pro_stueck"] - durchschnitt) / durchschnitt * 100

    # Farben: Rot wenn >15%, sonst Grün
    colors = ["#e74c3c" if x > 15 else "#27ae60" for x in df["abweichung_pct"]]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(
        df["standort_name"], df["abweichung_pct"], color=colors, edgecolor="black"
    )

    # Durchschnittslinie
    ax.axhline(y=0, color="black", linestyle="-", linewidth=1)
    ax.axhline(y=15, color="red", linestyle="--", linewidth=1.5, label="Grenzwert +15%")
    ax.axhline(y=-15, color="red", linestyle="--", linewidth=1.5)

    # Werte über Balken
    for bar, val in zip(bars, df["abweichung_pct"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{val:.1f}%",
            ha="center",
            fontsize=10,
            fontweight="bold",
        )

    ax.set_ylabel("Abweichung vom Durchschnitt (%)", fontsize=12)
    ax.set_xlabel("Standort", fontsize=12)
    ax.set_title(
        "Frage 1: Stromkostenintensität pro Standort (2024)\n"
        "Stückkosten (€/Einheit) - Abweichung vom Unternehmensdurchschnitt",
        fontsize=13,
        fontweight="bold",
    )
    ax.legend(loc="upper right")
    ax.set_ylim(-30, 50)
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()

    return fig


def plot_frage2():
    """
    Frage 2: Lastspitzen-Analyse
    Welche Linien/Schichten haben >500kW Spitzen?
    """
    df = run_query("frage2.sql")

    # Label erstellen
    df["label"] = df["linie_code"] + " (" + df["schicht"] + ")"

    fig, ax = plt.subplots(figsize=(12, 6))

    # Farben nach Schicht
    schicht_colors = {"Frueh": "#3498db", "Spaet": "#e74c3c", "Nacht": "#9b59b6"}
    colors = [schicht_colors.get(s, "#95a5a6") for s in df["schicht"]]

    bars = ax.barh(df["label"], df["anzahl_spitzen"], color=colors, edgecolor="black")

    # Grenzwert-Linie (6 Spitzen = Problemfall)
    ax.axvline(
        x=6, color="orange", linestyle="--", linewidth=2, label="Grenzwert (6 Spitzen)"
    )

    # Werte neben Balken
    for bar, val in zip(bars, df["anzahl_spitzen"]):
        ax.text(
            bar.get_width() + 5,
            bar.get_y() + bar.get_height() / 2,
            str(val),
            va="center",
            fontsize=10,
            fontweight="bold",
        )

    # Legende für Schichten
    from matplotlib.patches import Patch

    legend_elements = [
        Patch(facecolor="#3498db", label="Frühschicht"),
        Patch(facecolor="#e74c3c", label="Spätschicht"),
        Patch(facecolor="#9b59b6", label="Nachtschicht"),
    ]
    ax.legend(handles=legend_elements, loc="lower right")

    ax.set_xlabel("Anzahl Lastspitzen >500 kW (Q4 2024)", fontsize=12)
    ax.set_ylabel("Produktionslinie (Schicht)", fontsize=12)
    ax.set_title(
        "Frage 2: Lastspitzen-Analyse (Okt–Dez 2024)\n"
        "Top 10 Linien mit häufigsten 15-Min-Spitzen >500 kW",
        fontsize=13,
        fontweight="bold",
    )
    plt.tight_layout()

    return fig


def plot_frage3():
    """
    Frage 3: Lieferanten-Benchmarking
    Preisvergleich Lieferanten vs. Spotmarkt
    """
    df = run_query("frage3.sql")

    # Spotmarkt als Benchmark extrahieren
    spot_preis = df[df["name"] == "SPOTMARKT (Benchmark)"]["avg_preis_eur_kwh"].values[
        0
    ]
    lieferanten = df[df["name"] != "SPOTMARKT (Benchmark)"].copy()

    # Aufschlag berechnen
    lieferanten["aufschlag_pct"] = (
        (lieferanten["avg_preis_eur_kwh"] - spot_preis) / spot_preis * 100
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Chart 1: Absolute Preise
    colors = ["#3498db", "#e74c3c", "#f39c12", "#27ae60"]
    bars1 = ax1.bar(
        lieferanten["name"],
        lieferanten["avg_preis_eur_kwh"],
        color=colors[: len(lieferanten)],
        edgecolor="black",
    )
    ax1.axhline(
        y=spot_preis,
        color="black",
        linestyle="--",
        linewidth=2,
        label=f"Spotmarkt: {spot_preis:.4f} €/kWh",
    )

    for bar, val in zip(bars1, lieferanten["avg_preis_eur_kwh"]):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.005,
            f"{val:.4f}",
            ha="center",
            fontsize=10,
            fontweight="bold",
        )

    ax1.set_ylabel("Durchschnittspreis (€/kWh)", fontsize=12)
    ax1.set_xlabel("Lieferant", fontsize=12)
    ax1.set_title(
        "Durchschnittliche Einkaufspreise\n(2023–2024)", fontsize=12, fontweight="bold"
    )
    ax1.legend(loc="upper left")
    ax1.set_ylim(0, 0.35)
    plt.sca(ax1)
    plt.xticks(rotation=15, ha="right")

    # Chart 2: Aufschlag in %
    colors2 = [
        "#e74c3c" if x > 100 else "#f39c12" if x > 50 else "#27ae60"
        for x in lieferanten["aufschlag_pct"]
    ]
    bars2 = ax2.bar(
        lieferanten["name"],
        lieferanten["aufschlag_pct"],
        color=colors2,
        edgecolor="black",
    )

    for bar, val in zip(bars2, lieferanten["aufschlag_pct"]):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 3,
            f"+{val:.0f}%",
            ha="center",
            fontsize=10,
            fontweight="bold",
        )

    ax2.axhline(y=0, color="black", linestyle="-", linewidth=1)
    ax2.set_ylabel("Aufschlag vs. Spotmarkt (%)", fontsize=12)
    ax2.set_xlabel("Lieferant", fontsize=12)
    ax2.set_title(
        "Preisaufschlag gegenüber Spotmarkt\n(Höher = Teurer)",
        fontsize=12,
        fontweight="bold",
    )
    plt.sca(ax2)
    plt.xticks(rotation=15, ha="right")

    fig.suptitle(
        "Frage 3: Lieferanten-Benchmarking (2023–2024)",
        fontsize=14,
        fontweight="bold",
        y=0.98,
    )
    plt.tight_layout()

    return fig


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("Erstelle Visualisierungen...")

    # Frage 1
    fig1 = plot_frage1()
    fig1.savefig(OUTPUT_DIR / "frage1_stromkosten.png", dpi=150, bbox_inches="tight")
    print(f"✓ {OUTPUT_DIR / 'frage1_stromkosten.png'}")

    # Frage 2
    fig2 = plot_frage2()
    fig2.savefig(OUTPUT_DIR / "frage2_lastspitzen.png", dpi=150, bbox_inches="tight")
    print(f"✓ {OUTPUT_DIR / 'frage2_lastspitzen.png'}")

    # Frage 3
    fig3 = plot_frage3()
    fig3.savefig(OUTPUT_DIR / "frage3_lieferanten.png", dpi=150, bbox_inches="tight")
    print(f"✓ {OUTPUT_DIR / 'frage3_lieferanten.png'}")

    print(f"\nAlle Charts gespeichert in: {OUTPUT_DIR}")

    # Optional: Alle anzeigen
    plt.show()


if __name__ == "__main__":
    main()
