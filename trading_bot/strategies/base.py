from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class StrategyContext:
    symbol: str
    commodity: bool = True


class BaseStrategy:
    name = "base"

    def generate_signal(self, data: pd.DataFrame, context: StrategyContext) -> pd.Series:
        raise NotImplementedError
