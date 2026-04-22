import pandas as pd

from trading_bot.strategies.commodity_specialized import (
    clean_spark_spread,
    coffee_origin_dashboard,
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


def test_coffee_origin_dashboard_columns_and_signal():
    idx = pd.date_range("2024-01-01", periods=140, freq="D")
    arabica = pd.Series([180 + i * 0.2 for i in range(140)], index=idx)
    robusta = pd.Series([95 + i * 0.1 for i in range(140)], index=idx)
    data = pd.DataFrame(
        {
            "arabica_close": arabica,
            "robusta_close": robusta,
            "brazil_rainfall": [130 - min(i, 80) for i in range(140)],
            "brazil_temperature": [22 + min(i, 80) * 0.04 for i in range(140)],
            "brazil_drought_risk": [i / 140 for i in range(140)],
            "vietnam_rainfall": [110] * 140,
            "vietnam_temperature": [28] * 140,
            "colombia_rainfall": [120] * 140,
            "colombia_temperature": [22] * 140,
            "brl": [5.2 - i * 0.002 for i in range(140)],
            "usd_strength": [103 - i * 0.01 for i in range(140)],
            "arabica_nearby": arabica + 3,
            "arabica_deferred": arabica,
            "robusta_nearby": robusta + 1,
            "robusta_deferred": robusta,
            "certified_stocks": [900 - i for i in range(140)],
            "exports": [70 - i * 0.05 for i in range(140)],
            "freight": [20 + i * 0.03 for i in range(140)],
        },
        index=idx,
    )

    out = coffee_origin_dashboard(data)
    expected = {
        "arabica_robusta_ratio",
        "origin_supply_stress",
        "fx_pressure",
        "market_structure_pressure",
        "driver_score",
        "arabica_signal",
        "robusta_signal",
        "spread_signal",
        "signal",
    }
    assert expected.issubset(out.columns)
    assert set(out["signal"].unique()).issubset({0, 1})
