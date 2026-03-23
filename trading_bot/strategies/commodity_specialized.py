"""Enhanced commodity examples requested by user: copper momentum, spark spread, and a third metal (gold)."""

from __future__ import annotations

import pandas as pd


def copper_momentum_signal(close: pd.Series, short_window: int = 20, long_window: int = 100, adx_filter: bool = True) -> pd.DataFrame:
    df = pd.DataFrame({"close": close}).dropna().copy()
    df["ma_fast"] = df["close"].rolling(short_window).mean()
    df["ma_slow"] = df["close"].rolling(long_window).mean()
    trend_sig = (df["ma_fast"] > df["ma_slow"]).astype(int)

    if adx_filter:
        tr = df["close"].diff().abs().rolling(14).mean()
        momentum = df["close"].diff(14).abs()
        adx_like = 100 * (momentum / tr.replace(0, pd.NA))
        trend_sig = trend_sig.where(adx_like > 18, 0)

    df["signal"] = trend_sig.fillna(0)
    return df


def clean_spark_spread(power: pd.Series, gas: pd.Series, carbon: pd.Series, heat_rate: float = 7.2, emission_factor: float = 0.202) -> pd.Series:
    fuel_cost = gas * heat_rate
    carbon_cost = carbon * emission_factor
    return power - fuel_cost - carbon_cost


def spark_spread_signal(
    spread: pd.Series,
    entry_z: float = -1.0,
    exit_z: float = 0.2,
    lookback: int = 60,
) -> pd.DataFrame:
    df = pd.DataFrame({"spread": spread}).dropna().copy()
    mu = df["spread"].rolling(lookback).mean()
    sd = df["spread"].rolling(lookback).std()
    z = (df["spread"] - mu) / sd
    sig = pd.Series(0, index=df.index)
    pos = 0
    for i in range(len(df)):
        zv = z.iloc[i]
        if pd.isna(zv):
            sig.iloc[i] = pos
            continue
        if pos == 0 and zv < entry_z:
            pos = 1
        elif pos == 1 and zv > exit_z:
            pos = 0
        sig.iloc[i] = pos
    df["z"] = z
    df["signal"] = sig
    return df


def gold_real_rate_signal(gold_close: pd.Series, us10y_real_yield: pd.Series, lookback: int = 120) -> pd.DataFrame:
    df = pd.DataFrame({"gold": gold_close, "real_yield": us10y_real_yield}).dropna().copy()
    aligned = df["real_yield"].reindex(df.index).ffill()
    beta = -40  # stylized sensitivity, for interview demo purposes
    fair_value = df["gold"].rolling(lookback).mean() + beta * (aligned - aligned.rolling(lookback).mean())
    mispricing = (df["gold"] - fair_value) / df["gold"].rolling(lookback).std()

    sig = pd.Series(0, index=df.index)
    sig[mispricing < -1.0] = 1
    sig[mispricing > 0.75] = 0
    df["fair_value"] = fair_value
    df["mispricing_z"] = mispricing
    df["signal"] = sig.ffill().fillna(0)
    return df
