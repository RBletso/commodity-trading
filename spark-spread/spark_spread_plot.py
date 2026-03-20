import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

from spark_spread import (
    spark_spread, 
    dark_spread,
    DEFAULT_COAL_EMISSION_FACTOR
)

def run_analysis():
    # --- Fetch TTF gas ---
    ttf = yf.download('TTF=F', start='2024-01-01')['Close']
    ttf.name = 'Gas'
    ttf.dropna(inplace=True)

    # --- Synthetic coal price ---
    coal_price = ttf * 0.6
    coal_price.name = "Coal"

    # --- Parameters ---
    heat_rate_gas = 7.5
    carbon_price = 25.0
    emission_factor_gas = 0.2

    heat_rate_coal = 10.0
    emission_factor_coal = DEFAULT_COAL_EMISSION_FACTOR

    # --- Breakeven + Synthetic Power ---
    breakeven = (ttf * heat_rate_gas) + (carbon_price * emission_factor_gas)
    power_price = breakeven * 1.10

    # --- Spark Spread ---
    spark_vals = spark_spread(
        power_price, ttf, heat_rate_gas,
        carbon_price=carbon_price,
        emission_factor=emission_factor_gas
    )

    # --- Dark Spread ---
    dark_vals = dark_spread(
        power_price, coal_price, heat_rate_coal,
        carbon_price=carbon_price,
        emission_factor=emission_factor_coal
    )

    df = pd.DataFrame({
        "Gas": ttf,
        "Coal": coal_price,
        "Power": power_price,
        "Spark": spark_vals,
        "Dark": dark_vals
    })

    return df


def plot_all():
    df = run_analysis()

    # --- Spark Spread ---
    plt.figure(figsize=(12,4))
    plt.plot(df.index, df["Spark"], label="Spark Spread (Gas)", color="orange")
    plt.title("Spark Spread")
    plt.ylabel("€/MWh")
    plt.grid(True)
    plt.savefig("charts/spark_spread_curve.png")
    plt.close()

    # --- Dark Spread ---
    plt.figure(figsize=(12,4))
    plt.plot(df.index, df["Dark"], label="Dark Spread (Coal)", color="brown")
    plt.title("Dark Spread")
    plt.ylabel("€/MWh")
    plt.grid(True)
    plt.savefig("charts/dark_spread_curve.png")
    plt.close()

    # --- Combined ---
    plt.figure(figsize=(12,4))
    plt.plot(df.index, df["Spark"], label="Spark Spread (Gas)", color="orange")
    plt.plot(df.index, df["Dark"], label="Dark Spread (Coal)", color="brown")
    plt.title("Spark vs Dark Spread")
    plt.ylabel("€/MWh")
    plt.grid(True)
    plt.legend()
    plt.savefig("charts/spark_vs_dark.png")
    plt.close()

    print("Charts saved to /charts/")


if __name__ == "__main__":
    plot_all()