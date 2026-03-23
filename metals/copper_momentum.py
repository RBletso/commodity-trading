import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

from trading_bot.strategies.commodity_specialized import copper_momentum_signal


def run():
    copper = yf.download("HG=F", start="2022-01-01")["Close"].dropna().squeeze()
    df = copper_momentum_signal(copper, short_window=20, long_window=100, adx_filter=True)
    df["ret"] = df["close"].pct_change().fillna(0)
    df["strat_ret"] = df["signal"].shift(1).fillna(0) * df["ret"]
    df["cum_market"] = (1 + df["ret"]).cumprod()
    df["cum_strategy"] = (1 + df["strat_ret"]).cumprod()

    print(df[["close", "ma_fast", "ma_slow", "signal"]].tail(10))
    print(f"Signal: {'LONG' if df['signal'].iloc[-1] == 1 else 'FLAT'}")
    print(f"Strategy return: {(df['cum_strategy'].iloc[-1]-1)*100:.2f}%")
    print(f"Buy&hold return: {(df['cum_market'].iloc[-1]-1)*100:.2f}%")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    ax1.plot(df.index, df["close"], label="Copper", color="steelblue")
    ax1.plot(df.index, df["ma_fast"], label="MA20", color="orange")
    ax1.plot(df.index, df["ma_slow"], label="MA100", color="red")
    ax1.fill_between(df.index, df["close"].min(), df["close"].max(), where=df["signal"] == 1, alpha=0.1, color="green")
    ax1.legend()
    ax1.grid(alpha=0.3)

    ax2.plot(df.index, df["cum_strategy"], label="Strategy", color="purple")
    ax2.plot(df.index, df["cum_market"], label="Market", color="gray")
    ax2.legend()
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("copper_momentum.png")
    print("Saved copper_momentum.png")


if __name__ == "__main__":
    run()
