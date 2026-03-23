from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class BacktestResult:
    equity_curve: pd.Series
    returns: pd.Series
    sharpe: float
    total_return: float
    max_drawdown: float


class Backtester:
    def __init__(self, commission_bps: float = 1.0, slippage_bps: float = 2.0):
        self.commission_bps = commission_bps / 10_000
        self.slippage_bps = slippage_bps / 10_000

    def run(self, prices: pd.Series, signal: pd.Series, initial_capital: float = 100_000.0) -> BacktestResult:
        df = pd.DataFrame({"price": prices, "signal": signal}).dropna().copy()
        df["ret"] = df["price"].pct_change().fillna(0.0)
        trades = df["signal"].diff().abs().fillna(0.0)
        cost = trades * (self.commission_bps + self.slippage_bps)
        df["strategy_ret"] = df["signal"].shift(1).fillna(0.0) * df["ret"] - cost
        equity_curve = initial_capital * (1 + df["strategy_ret"]).cumprod()
        roll_max = equity_curve.cummax()
        drawdown = equity_curve / roll_max - 1
        sharpe = 0.0
        std = df["strategy_ret"].std()
        if std > 0:
            sharpe = (df["strategy_ret"].mean() / std) * (252**0.5)
        return BacktestResult(
            equity_curve=equity_curve,
            returns=df["strategy_ret"],
            sharpe=float(sharpe),
            total_return=float(equity_curve.iloc[-1] / initial_capital - 1),
            max_drawdown=float(drawdown.min()),
        )
