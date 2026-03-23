import pandas as pd

from trading_bot.strategies.base import StrategyContext
from trading_bot.strategies.library import STRATEGY_REGISTRY, build_strategy


def _sample_df(n=200):
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    close = pd.Series([100 + (i * 0.05) for i in range(n)], index=idx)
    return pd.DataFrame(
        {
            "close": close,
            "high": close * 1.01,
            "low": close * 0.99,
            "volume": 1000,
            "pair_close": close * 0.98,
        },
        index=idx,
    )


def test_registry_has_ten_strategies():
    assert len(STRATEGY_REGISTRY) == 10


def test_all_strategies_emit_series():
    df = _sample_df()
    ctx = StrategyContext(symbol="HG_F")
    for name in STRATEGY_REGISTRY:
        s = build_strategy(name)
        sig = s.generate_signal(df, ctx)
        assert len(sig) == len(df)
        assert set(sig.dropna().unique()).issubset({0, 1})
