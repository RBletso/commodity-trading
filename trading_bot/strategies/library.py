from __future__ import annotations

import pandas as pd

from .base import BaseStrategy, StrategyContext


def _sma(s: pd.Series, n: int) -> pd.Series:
    return s.rolling(n).mean()


def _ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def _rsi(close: pd.Series, n: int = 14) -> pd.Series:
    delta = close.diff()
    up = delta.clip(lower=0).rolling(n).mean()
    down = -delta.clip(upper=0).rolling(n).mean()
    rs = up / down.replace(0, pd.NA)
    return 100 - (100 / (1 + rs))


class TrendSMA(BaseStrategy):
    name = "trend_sma"

    def generate_signal(self, data: pd.DataFrame, context: StrategyContext) -> pd.Series:
        fast, slow = _sma(data["close"], 20), _sma(data["close"], 50)
        return (fast > slow).astype(int)


class EMAcrossover(BaseStrategy):
    name = "ema_crossover"

    def generate_signal(self, data: pd.DataFrame, context: StrategyContext) -> pd.Series:
        fast, slow = _ema(data["close"], 12), _ema(data["close"], 26)
        return (fast > slow).astype(int)


class RSIMeanReversion(BaseStrategy):
    name = "rsi_mean_reversion"

    def generate_signal(self, data: pd.DataFrame, context: StrategyContext) -> pd.Series:
        rsi = _rsi(data["close"], 14)
        sig = pd.Series(0, index=data.index)
        sig[rsi < 30] = 1
        sig[rsi > 70] = 0
        return sig.ffill().fillna(0)


class BollingerReversion(BaseStrategy):
    name = "bollinger_reversion"

    def generate_signal(self, data: pd.DataFrame, context: StrategyContext) -> pd.Series:
        mid = _sma(data["close"], 20)
        std = data["close"].rolling(20).std()
        lower = mid - 2 * std
        upper = mid + 2 * std
        sig = pd.Series(0, index=data.index)
        sig[data["close"] < lower] = 1
        sig[data["close"] > upper] = 0
        return sig.ffill().fillna(0)


class DonchianBreakout(BaseStrategy):
    name = "donchian_breakout"

    def generate_signal(self, data: pd.DataFrame, context: StrategyContext) -> pd.Series:
        hi = data["high"].rolling(20).max()
        lo = data["low"].rolling(10).min()
        sig = pd.Series(0, index=data.index)
        sig[data["close"] > hi.shift(1)] = 1
        sig[data["close"] < lo.shift(1)] = 0
        return sig.ffill().fillna(0)


class MACDTrend(BaseStrategy):
    name = "macd_trend"

    def generate_signal(self, data: pd.DataFrame, context: StrategyContext) -> pd.Series:
        macd = _ema(data["close"], 12) - _ema(data["close"], 26)
        signal = _ema(macd, 9)
        return (macd > signal).astype(int)


class ADXTrendFilter(BaseStrategy):
    name = "adx_trend_filter"

    def generate_signal(self, data: pd.DataFrame, context: StrategyContext) -> pd.Series:
        tr = (data["high"] - data["low"]).rolling(14).mean()
        momentum = data["close"].diff(10).abs()
        adx_like = 100 * (momentum / tr.replace(0, pd.NA))
        return (adx_like > 25).astype(int).fillna(0)


class CalendarSeasonal(BaseStrategy):
    name = "calendar_seasonal"

    def generate_signal(self, data: pd.DataFrame, context: StrategyContext) -> pd.Series:
        # Simple commodity-aware seasonality proxy: long Nov-Apr.
        months = data.index.month
        return ((months >= 11) | (months <= 4)).astype(int)


class PairSpreadZScore(BaseStrategy):
    name = "pair_spread_zscore"

    def generate_signal(self, data: pd.DataFrame, context: StrategyContext) -> pd.Series:
        # Requires column pair_close for commodity spread pair.
        spread = data["close"] - data["pair_close"]
        z = (spread - spread.rolling(30).mean()) / spread.rolling(30).std()
        sig = pd.Series(0, index=data.index)
        sig[z < -1.5] = 1
        sig[z > 0.0] = 0
        return sig.ffill().fillna(0)


class VolumePriceBreakout(BaseStrategy):
    name = "volume_price_breakout"

    def generate_signal(self, data: pd.DataFrame, context: StrategyContext) -> pd.Series:
        vol_ma = data["volume"].rolling(20).mean()
        price_hi = data["high"].rolling(20).max()
        return ((data["close"] > price_hi.shift(1)) & (data["volume"] > 1.3 * vol_ma)).astype(int)


STRATEGY_REGISTRY = {
    cls.name: cls
    for cls in [
        TrendSMA,
        EMAcrossover,
        RSIMeanReversion,
        BollingerReversion,
        DonchianBreakout,
        MACDTrend,
        ADXTrendFilter,
        CalendarSeasonal,
        PairSpreadZScore,
        VolumePriceBreakout,
    ]
}


def build_strategy(name: str) -> BaseStrategy:
    if name not in STRATEGY_REGISTRY:
        raise KeyError(f"Unknown strategy '{name}'. Available: {', '.join(sorted(STRATEGY_REGISTRY))}")
    return STRATEGY_REGISTRY[name]()
