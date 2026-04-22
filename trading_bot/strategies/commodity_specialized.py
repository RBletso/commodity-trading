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


def _zscore(series: pd.Series, lookback: int) -> pd.Series:
    mean = series.rolling(lookback, min_periods=max(5, lookback // 4)).mean()
    std = series.rolling(lookback, min_periods=max(5, lookback // 4)).std()
    return ((series - mean) / std.replace(0, pd.NA)).fillna(0.0)


def _optional_z(data: pd.DataFrame, column: str, lookback: int) -> pd.Series:
    if column not in data:
        return pd.Series(0.0, index=data.index)
    return _zscore(data[column].astype(float), lookback)


def coffee_origin_dashboard(data: pd.DataFrame, lookback: int = 60) -> pd.DataFrame:
    """Build a coffee dashboard and simple long/flat signal from origin drivers.

    Expected core columns are ``arabica_close`` and ``robusta_close``. Optional
    columns add signal detail: weather by origin, FX, curve spreads, freight,
    certified stocks, and exports. ``brl`` is treated as USD/BRL, where a higher
    value means a weaker Brazilian real.
    """

    df = data.copy().sort_index()
    if "arabica_close" not in df and "close" in df:
        df["arabica_close"] = df["close"]
    if "robusta_close" not in df and "pair_close" in df:
        df["robusta_close"] = df["pair_close"]
    if "arabica_close" not in df or "robusta_close" not in df:
        raise KeyError("coffee_origin_dashboard requires arabica_close and robusta_close columns")

    out = pd.DataFrame(index=df.index)
    out["arabica_close"] = df["arabica_close"].astype(float)
    out["robusta_close"] = df["robusta_close"].astype(float)
    out["arabica_robusta_ratio"] = out["arabica_close"] / out["robusta_close"].replace(0, pd.NA)

    brazil_weather = (
        -_optional_z(df, "brazil_rainfall", lookback)
        + _optional_z(df, "brazil_temperature", lookback)
        + _optional_z(df, "brazil_drought_risk", lookback)
        + _optional_z(df, "brazil_frost_risk", lookback)
    )
    vietnam_weather = (
        -_optional_z(df, "vietnam_rainfall", lookback)
        + _optional_z(df, "vietnam_temperature", lookback)
        + _optional_z(df, "vietnam_drought_risk", lookback)
    )
    colombia_weather = (
        -_optional_z(df, "colombia_rainfall", lookback)
        + _optional_z(df, "colombia_temperature", lookback)
        + _optional_z(df, "colombia_drought_risk", lookback)
    )

    out["brazil_weather_stress"] = brazil_weather
    out["vietnam_weather_stress"] = vietnam_weather
    out["colombia_weather_stress"] = colombia_weather
    out["origin_supply_stress"] = (0.50 * brazil_weather) + (0.35 * vietnam_weather) + (0.15 * colombia_weather)

    out["fx_pressure"] = (
        -_optional_z(df, "brl", lookback)
        - 0.50 * _optional_z(df, "usd_strength", lookback)
        - 0.25 * _optional_z(df, "vnd_proxy", lookback)
    )

    if {"arabica_nearby", "arabica_deferred"}.issubset(df.columns):
        out["arabica_spread"] = df["arabica_nearby"].astype(float) - df["arabica_deferred"].astype(float)
    else:
        out["arabica_spread"] = 0.0
    if {"robusta_nearby", "robusta_deferred"}.issubset(df.columns):
        out["robusta_spread"] = df["robusta_nearby"].astype(float) - df["robusta_deferred"].astype(float)
    else:
        out["robusta_spread"] = 0.0

    out["market_structure_pressure"] = _zscore(out["arabica_spread"], lookback) + 0.7 * _zscore(out["robusta_spread"], lookback)
    out["stock_pressure"] = -_optional_z(df, "certified_stocks", lookback)
    out["export_pressure"] = -_optional_z(df, "exports", lookback)
    out["freight_pressure"] = _optional_z(df, "freight", lookback)

    out["driver_score"] = (
        0.35 * out["origin_supply_stress"]
        + 0.20 * out["fx_pressure"]
        + 0.20 * out["market_structure_pressure"]
        + 0.10 * out["stock_pressure"]
        + 0.10 * out["export_pressure"]
        + 0.05 * out["freight_pressure"]
    )

    price_trend = _zscore(out["arabica_close"].pct_change(20).fillna(0.0), lookback)
    out["arabica_signal"] = ((out["driver_score"] > 0.35) & (price_trend > -0.75)).astype(int)
    out["robusta_signal"] = ((out["driver_score"] > 0.20) & (out["vietnam_weather_stress"] > 0.25)).astype(int)
    out["spread_signal"] = (out["brazil_weather_stress"] > out["vietnam_weather_stress"]).astype(int)
    out["signal"] = out["arabica_signal"]
    return out.fillna(0.0)
