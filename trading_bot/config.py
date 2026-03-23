from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class RiskConfig:
    max_risk_per_trade: float = 0.01
    max_portfolio_risk: float = 0.05
    max_leverage: float = 2.0
    stop_loss_atr_multiplier: float = 2.0


@dataclass
class MT5Config:
    login: int | None = None
    password: str | None = None
    server: str | None = None
    path: str | None = None


@dataclass
class BotConfig:
    symbols: list[str] = field(default_factory=lambda: ["XAUUSD", "XAGUSD", "HG_F"])
    timeframe: str = "D1"
    initial_capital: float = 100_000.0
    commission_bps: float = 1.0
    slippage_bps: float = 2.0
    risk: RiskConfig = field(default_factory=RiskConfig)
    mt5: MT5Config = field(default_factory=MT5Config)


def _merge_dict(defaults: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    out = defaults.copy()
    for k, v in updates.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge_dict(out[k], v)
        else:
            out[k] = v
    return out


def load_config(path: str | Path) -> BotConfig:
    raw = yaml.safe_load(Path(path).read_text()) or {}
    default_raw = {
        "symbols": ["XAUUSD", "XAGUSD", "HG_F"],
        "timeframe": "D1",
        "initial_capital": 100_000.0,
        "commission_bps": 1.0,
        "slippage_bps": 2.0,
        "risk": RiskConfig().__dict__,
        "mt5": MT5Config().__dict__,
    }
    data = _merge_dict(default_raw, raw)
    return BotConfig(
        symbols=data["symbols"],
        timeframe=data["timeframe"],
        initial_capital=float(data["initial_capital"]),
        commission_bps=float(data["commission_bps"]),
        slippage_bps=float(data["slippage_bps"]),
        risk=RiskConfig(**data["risk"]),
        mt5=MT5Config(**data["mt5"]),
    )
