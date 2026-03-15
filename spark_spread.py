import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

# --- FETCH DATA ---
ttf = yf.download('TTF=F', start='2024-01-01')['Close']
ttf.name = 'TTF'

# --- PARAMETERS ---
heat_rate = 7.5
carbon_price = 25.0
emission_factor = 0.2
long_entry = 30.0
long_exit = 40.0

# --- CALCULATE SPREAD ---
breakeven = (ttf * heat_rate) + (carbon_price * emission_factor)
power_price = breakeven * 1.10
spark_spread = power_price - (ttf * heat_rate) - (carbon_price * emission_factor)

# --- DATAFRAME ---
df = pd.DataFrame({
    'TTF': ttf.squeeze(),
    'Breakeven_Power': breakeven.squeeze(),
    'Power_Price': power_price.squeeze(),
    'Spark_Spread': spark_spread.squeeze()
})

print(df.tail(10))
print(f"\nAverage Spark Spread: {df['Spark_Spread'].mean():.2f} EUR/MWh")
print(f"Max Spark Spread: {df['Spark_Spread'].max():.2f} EUR/MWh")
print(f"Min Spark Spread: {df['Spark_Spread'].min():.2f} EUR/MWh")

# --- TRADING SIGNAL ---
df['Signal'] = 0
position = 0

for i in range(len(df)):
    if position == 0 and df['Spark_Spread'].iloc[i] < long_entry:
        position = 1
    elif position == 1 and df['Spark_Spread'].iloc[i] > long_exit:
        position = 0
    df.loc[df.index[i], 'Signal'] = position

# --- P&L ---
df['Daily_PnL'] = df['Signal'].shift(1) * df['Spark_Spread'].diff()
df['Cumulative_PnL'] = df['Daily_PnL'].cumsum()

print("\nTrade summary:")
print(f"Total days in market: {df['Signal'].sum()}")
print(f"Total cumulative PnL: {df['Cumulative_PnL'].iloc[-1]:.2f} EUR/MWh")
print(f"Number of signals triggered: {df['Signal'].diff().eq(1).sum()}")

# --- PLOT ---
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

ax1.plot(df.index, df['TTF'], color='steelblue', linewidth=1)
ax1.set_ylabel('EUR/MWh')
ax1.set_title('TTF Gas Price')
ax1.grid(True, alpha=0.3)

ax2.plot(df.index, df['Spark_Spread'], color='orange', linewidth=1, label='Spark Spread')
ax2.axhline(y=long_entry, color='green', linestyle='--', linewidth=0.8, label=f'Entry ({long_entry})')
ax2.axhline(y=long_exit, color='red', linestyle='--', linewidth=0.8, label=f'Exit ({long_exit})')
ax2.fill_between(df.index, df['Spark_Spread'], long_entry,
                  where=(df['Signal'] == 1), alpha=0.2, color='green', label='In trade')
ax2.set_ylabel('EUR/MWh')
ax2.set_title('Spark Spread + Signal')
ax2.legend(fontsize=8)
ax2.grid(True, alpha=0.3)

ax3.plot(df.index, df['Cumulative_PnL'], color='purple', linewidth=1)
ax3.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
ax3.fill_between(df.index, df['Cumulative_PnL'], 0,
                  where=(df['Cumulative_PnL'] > 0), alpha=0.3, color='green')
ax3.fill_between(df.index, df['Cumulative_PnL'], 0,
                  where=(df['Cumulative_PnL'] < 0), alpha=0.3, color='red')
ax3.set_ylabel('EUR/MWh')
ax3.set_title('Cumulative P&L')
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('spark_spread.png')
print("Chart saved")