import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

from trading_bot.strategies.commodity_specialized import clean_spark_spread, spark_spread_signal


def run_analysis():
    gas = yf.download("TTF=F", start="2023-01-01")["Close"].dropna().squeeze()
    power = yf.download("DEBAS=F", start="2023-01-01")["Close"].dropna().squeeze()
    carbon = yf.download("CO2.L", start="2023-01-01")["Close"].dropna().squeeze()

    df = pd.concat([gas.rename("gas"), power.rename("power"), carbon.rename("carbon")], axis=1).dropna()
    df["spark"] = clean_spark_spread(df["power"], df["gas"], df["carbon"], heat_rate=7.2, emission_factor=0.202)
    sig_df = spark_spread_signal(df["spark"], entry_z=-1.0, exit_z=0.3, lookback=60)
    df = df.join(sig_df[["z", "signal"]], how="left")
    df["pnl"] = df["signal"].shift(1).fillna(0) * df["spark"].diff().fillna(0)
    df["cum_pnl"] = df["pnl"].cumsum()
    return df


def plot_all():
    df = run_analysis()

    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    axes[0].plot(df.index, df["spark"], label="Clean Spark Spread", color="orange")
    axes[0].set_title("Clean Spark Spread")
    axes[0].grid(alpha=0.3)

    axes[1].plot(df.index, df["z"], label="Z-Score", color="teal")
    axes[1].axhline(-1.0, linestyle="--", color="green")
    axes[1].axhline(0.3, linestyle="--", color="red")
    axes[1].fill_between(df.index, -3, 3, where=df["signal"] == 1, color="green", alpha=0.15)
    axes[1].set_title("Signal Regime")
    axes[1].grid(alpha=0.3)

    axes[2].plot(df.index, df["cum_pnl"], label="Cumulative PnL", color="purple")
    axes[2].axhline(0, color="black", linestyle="--", linewidth=0.8)
    axes[2].set_title("Long Spark Mean Reversion PnL")
    axes[2].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("spark_spread.png")
    print("Saved spark_spread.png")


if __name__ == "__main__":
    plot_all()
