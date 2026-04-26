from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

from trading_bot.strategies.commodity_specialized import coffee_origin_dashboard


def run():
    arabica = yf.download("KC=F", start="2023-01-01")["Close"].dropna().squeeze()
    if arabica.empty:
        raise ValueError("No Arabica data downloaded for KC=F")

    # Robusta is not consistently available across free endpoints, so this uses
    # a simple scaled proxy to keep the demo script runnable until a direct feed
    # is wired in.
    robusta_proxy = (arabica * 0.55).rename("robusta_close")

    df = pd.DataFrame(
        {
            "arabica_close": arabica.rename("arabica_close"),
            "robusta_close": robusta_proxy,
        }
    ).dropna()

    rolling_mean = df["arabica_close"].rolling(30, min_periods=5).mean()
    df["brazil_rainfall"] = (140 - (df["arabica_close"] - rolling_mean).fillna(0).clip(lower=-15, upper=15)).clip(lower=90)
    df["brazil_temperature"] = 23 + df["arabica_close"].pct_change(10).fillna(0).rolling(5, min_periods=1).mean() * 40
    df["brazil_drought_risk"] = df["arabica_close"].pct_change(20).fillna(0).rolling(10, min_periods=1).mean().clip(lower=0) * 25
    df["brazil_frost_risk"] = 0.0
    df["vietnam_rainfall"] = 115.0
    df["vietnam_temperature"] = 28.0
    df["colombia_rainfall"] = 120.0
    df["colombia_temperature"] = 22.0
    df["brl"] = yf.download("BRL=X", start="2023-01-01")["Close"].reindex(df.index).ffill().bfill().squeeze()
    df["usd_strength"] = yf.download("DX-Y.NYB", start="2023-01-01")["Close"].reindex(df.index).ffill().bfill().squeeze()
    df["arabica_nearby"] = df["arabica_close"]
    df["arabica_deferred"] = df["arabica_close"].rolling(20, min_periods=1).mean() * 0.995
    df["robusta_nearby"] = df["robusta_close"]
    df["robusta_deferred"] = df["robusta_close"].rolling(20, min_periods=1).mean() * 0.995

    dashboard = coffee_origin_dashboard(df)

    latest = dashboard.iloc[-1]
    print(dashboard[["arabica_close", "robusta_close", "driver_score", "signal"]].tail(10))
    print(f"Current Arabica signal: {'LONG' if latest['arabica_signal'] == 1 else 'FLAT'}")
    print(f"Current Robusta signal: {'LONG' if latest['robusta_signal'] == 1 else 'FLAT'}")
    print(f"Current spread view: {'ARABICA OVER ROBUSTA' if latest['spread_signal'] == 1 else 'NEUTRAL'}")

    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    axes[0].plot(dashboard.index, dashboard["arabica_close"], label="Arabica", color="saddlebrown")
    axes[0].plot(dashboard.index, dashboard["robusta_close"], label="Robusta Proxy", color="darkgreen")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    axes[1].plot(dashboard.index, dashboard["origin_supply_stress"], label="Origin Supply Stress", color="firebrick")
    axes[1].plot(dashboard.index, dashboard["fx_pressure"], label="FX Pressure", color="steelblue")
    axes[1].plot(dashboard.index, dashboard["market_structure_pressure"], label="Curve Pressure", color="darkorange")
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    axes[2].plot(dashboard.index, dashboard["driver_score"], label="Driver Score", color="purple")
    axes[2].axhline(0.35, linestyle="--", color="green")
    axes[2].fill_between(dashboard.index, dashboard["driver_score"].min(), dashboard["driver_score"].max(), where=dashboard["signal"] == 1, color="green", alpha=0.12)
    axes[2].legend()
    axes[2].grid(alpha=0.3)

    plt.tight_layout()
    output_path = Path(__file__).with_name("coffee_origin.png")
    plt.savefig(output_path)
    print(f"Saved {output_path}")


if __name__ == "__main__":
    run()
