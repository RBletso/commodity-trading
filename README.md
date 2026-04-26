# Commodity Trading Bot Framework

Python framework for swing-trading commodities with:
- MT5 integration wrapper
- Risk management and position sizing
- Logging setup
- Backtesting engine
- Strategy module with **11 optional swing strategies**
- YAML config system
- Tests

## Project Layout

- `energy/` → energy-specific scripts and notebooks (`spark_spread.py`, `spark_spread_plot.py`)
- `metals/` → metal-specific scripts (`copper_momentum.py`, `gold_real_rate.py`)
- `softs/` → soft commodity scripts (`coffee_origin.py`)
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
python energy/spark_spread_plot.py
python softs/coffee_origin.py
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
11. Coffee Origin Driver

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

### 4) Coffee Origin Dashboard (Arabica vs Robusta)
- Compares ICE Arabica and ICE/LIFFE Robusta price behavior
- Tracks origin drivers for Brazil, Vietnam, and Colombia
- Includes FX pressure from BRL, USD strength, and optional VND proxy
- Uses weather stress from rainfall, temperature, drought risk, and frost risk
- Adds market structure through nearby vs deferred futures spreads
- Optional pressure inputs: freight, certified stocks, and exports
- Produces dashboard columns plus simple `arabica_signal`, `robusta_signal`, `spread_signal`, and final `signal`

Expected columns for the richer model:

```text
arabica_close, robusta_close,
brazil_rainfall, brazil_temperature, brazil_drought_risk, brazil_frost_risk,
vietnam_rainfall, vietnam_temperature, vietnam_drought_risk,
colombia_rainfall, colombia_temperature, colombia_drought_risk,
brl, usd_strength, vnd_proxy,
arabica_nearby, arabica_deferred, robusta_nearby, robusta_deferred,
freight, certified_stocks, exports
```

Only `arabica_close` and `robusta_close` are required. Missing optional columns are treated as neutral.

`softs/coffee_origin.py` gives you a simple demo runner and plot for the coffee dashboard. It uses live Arabica data plus a temporary Robusta proxy until you wire in a dedicated Robusta feed.

## Notes
- MT5 client gracefully degrades if `MetaTrader5` package is unavailable.
- This is a framework skeleton for research/interview prep; productionization needs broker safeguards.
