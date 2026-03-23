import pandas as pd

from trading_bot.strategies.commodity_specialized import (
    clean_spark_spread,
    copper_momentum_signal,
    gold_real_rate_signal,
    spark_spread_signal,
)


def test_copper_signal_columns():
    idx = pd.date_range("2024-01-01", periods=220, freq="D")
    close = pd.Series([3.5 + i * 0.001 for i in range(220)], index=idx)
    out = copper_momentum_signal(close)
    assert {"ma_fast", "ma_slow", "signal"}.issubset(out.columns)


def test_clean_spark_formula():
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    s = clean_spark_spread(
        power=pd.Series([100] * 5, index=idx),
        gas=pd.Series([10] * 5, index=idx),
        carbon=pd.Series([50] * 5, index=idx),
    )
    assert (s.round(3) == 17.9).all()


def test_spark_zscore_signal():
    idx = pd.date_range("2024-01-01", periods=140, freq="D")
    spread = pd.Series([30 + ((i % 20) - 10) * 0.5 for i in range(140)], index=idx)
    out = spark_spread_signal(spread)
    assert "signal" in out.columns


def test_gold_signal():
    idx = pd.date_range("2024-01-01", periods=240, freq="D")
    gold = pd.Series([1900 + i * 0.2 for i in range(240)], index=idx)
    ry = pd.Series([1.5 + ((-1) ** i) * 0.01 for i in range(240)], index=idx)
    out = gold_real_rate_signal(gold, ry)
    assert "signal" in out.columns
