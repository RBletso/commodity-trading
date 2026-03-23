import pandas as pd

from trading_bot.backtesting import Backtester


def test_backtester_runs():
    idx = pd.date_range("2024-01-01", periods=120, freq="D")
    prices = pd.Series(100 + pd.Series(range(120)).values * 0.1, index=idx)
    signal = pd.Series([1] * 120, index=idx)
    bt = Backtester()
    res = bt.run(prices, signal)
    assert res.equity_curve.iloc[-1] > 0
    assert -1 <= res.max_drawdown <= 0
