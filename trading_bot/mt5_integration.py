from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)

try:
    import MetaTrader5 as mt5
except ImportError:  # pragma: no cover
    mt5 = None


TIMEFRAME_MAP = {
    "M1": 1,
    "M5": 5,
    "M15": 15,
    "H1": 60,
    "D1": 1440,
}


@dataclass
class MT5Client:
    login: int | None = None
    password: str | None = None
    server: str | None = None
    path: str | None = None

    def connect(self) -> bool:
        if mt5 is None:
            logger.warning("MetaTrader5 package not installed; MT5 mode disabled.")
            return False
        ok = mt5.initialize(path=self.path, login=self.login, password=self.password, server=self.server)
        if not ok:
            logger.error("MT5 initialize failed: %s", mt5.last_error())
        return bool(ok)

    def shutdown(self) -> None:
        if mt5 is not None:
            mt5.shutdown()

    def get_rates(self, symbol: str, timeframe: str, start: datetime, end: datetime) -> pd.DataFrame:
        if mt5 is None:
            raise RuntimeError("MetaTrader5 package unavailable.")
        tf = getattr(mt5, f"TIMEFRAME_{timeframe}", None)
        if tf is None:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        rates = mt5.copy_rates_range(symbol, tf, start, end)
        if rates is None:
            raise RuntimeError(f"No MT5 data for {symbol}")
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df.set_index("time")
