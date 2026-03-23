from __future__ import annotations

import argparse
from dataclasses import asdict

import pandas as pd

from .backtesting import Backtester
from .config import load_config
from .logging_utils import setup_logging
from .risk import RiskManager
from .strategies.base import StrategyContext
from .strategies.library import build_strategy


def run(csv_path: str, strategy_name: str, config_path: str) -> dict:
    cfg = load_config(config_path)
    setup_logging()

    data = pd.read_csv(csv_path, parse_dates=["date"]).set_index("date")
    strategy = build_strategy(strategy_name)
    signal = strategy.generate_signal(data, StrategyContext(symbol="GENERIC"))

    bt = Backtester(cfg.commission_bps, cfg.slippage_bps)
    result = bt.run(data["close"], signal, cfg.initial_capital)

    risk = RiskManager(
        max_risk_per_trade=cfg.risk.max_risk_per_trade,
        max_portfolio_risk=cfg.risk.max_portfolio_risk,
        max_leverage=cfg.risk.max_leverage,
    )

    return {
        "config": asdict(cfg),
        "strategy": strategy_name,
        "total_return": result.total_return,
        "sharpe": result.sharpe,
        "max_drawdown": result.max_drawdown,
        "example_position_size": risk.position_size(
            equity=cfg.initial_capital,
            entry=float(data["close"].iloc[-1]),
            stop=float(data["close"].iloc[-1] * 0.98),
            contract_size=1.0,
        ),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--strategy", default="trend_sma")
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()
    print(run(args.csv, args.strategy, args.config))
