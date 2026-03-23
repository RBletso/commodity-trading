# Commodity Trading Bot Framework

Python framework for swing-trading commodities with:
- MT5 integration wrapper
- Risk management and position sizing
- Logging setup
- Backtesting engine
- Strategy module with **10 optional swing strategies**
- YAML config system
- Tests

## Project Layout

- `spark-spread/` → spark spread models/scripts (kept together in original folder layout)
- `metals/` → metal-specific scripts (`copper_momentum.py`, `gold_real_rate.py`)
- `trading_bot/` → reusable bot framework modules (config, risk, MT5, backtesting, strategies)

## Quick Start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

Run a generic backtest:

```bash
python -m trading_bot.runner --csv data/sample_ohlcv.csv --strategy trend_sma --config config.yaml
```

Run commodity scripts:

```bash
python metals/copper_momentum.py
python metals/gold_real_rate.py
python spark-spread/spark_spread_plot.py
```

## Included Swing Strategies (optional, commodity-friendly)

1. SMA Trend (20/50)
2. EMA Crossover (12/26)
3. RSI Mean Reversion
4. Bollinger Band Reversion
5. Donchian Breakout
6. MACD Trend
7. ADX Trend Filter
8. Calendar Seasonal (Nov–Apr proxy)
9. Pair Spread Z-Score
10. Volume+Price Breakout

## Enhanced Commodity Modules

### 1) Copper Momentum (improved)
- Uses slower trend confirmation (20/100)
- Optional ADX-like filter to reduce whipsaws

### 2) Spark Spread (improved)
- Uses **clean spark spread** formula with explicit carbon term:
  `Power - (Gas * HeatRate) - (Carbon * EmissionFactor)`
- Z-score signal logic for entry/exit instead of static thresholds

### 3) Gold vs Real Yield (new metal module)
- Gold mean-reversion around rolling fair value linked to US 10Y real yield
- Interview-friendly macro + technical hybrid example

## Notes
- MT5 client gracefully degrades if `MetaTrader5` package is unavailable.
- This is a framework skeleton for research/interview prep; productionization needs broker safeguards.
