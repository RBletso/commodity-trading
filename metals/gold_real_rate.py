import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

from trading_bot.strategies.commodity_specialized import gold_real_rate_signal


def run():
    gold = yf.download("GC=F", start="2021-01-01")["Close"].dropna().squeeze()
    tips = yf.download("^TNX", start="2021-01-01")["Close"].dropna().squeeze()  # nominal proxy

    df = gold_real_rate_signal(gold_close=gold, us10y_real_yield=tips, lookback=120)
    df["ret"] = df["gold"].pct_change().fillna(0)
    df["strat_ret"] = df["signal"].shift(1).fillna(0) * df["ret"]
    df["cum"] = (1 + df["strat_ret"]).cumprod()

    print(df[["gold", "fair_value", "mispricing_z", "signal"]].tail(10))

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    axes[0].plot(df.index, df["gold"], label="Gold", color="goldenrod")
    axes[0].plot(df.index, df["fair_value"], label="Fair Value", color="slateblue")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    axes[1].plot(df.index, df["mispricing_z"], label="Mispricing Z", color="teal")
    axes[1].axhline(-1.0, linestyle="--", color="green")
    axes[1].axhline(0.75, linestyle="--", color="red")
    axes[1].fill_between(df.index, -3, 3, where=df["signal"] == 1, color="green", alpha=0.15)
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("gold_real_rate.png")
    print("Saved gold_real_rate.png")


if __name__ == "__main__":
    run()
