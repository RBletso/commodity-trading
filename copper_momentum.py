import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

# --- FETCH DATA ---
copper = yf.download('HG=F', start='2024-01-01')['Close']
copper.name = 'Copper'

# --- PARAMETERS ---
short_window = 20   # 20 day moving average
long_window = 50    # 50 day moving average

# --- MOVING AVERAGES ---
df = pd.DataFrame({'Copper': copper.squeeze()})
df['MA20'] = df['Copper'].rolling(window=short_window).mean()
df['MA50'] = df['Copper'].rolling(window=long_window).mean()

# --- SIGNAL ---
# Buy when MA20 crosses above MA50 (momentum building)
# Sell when MA20 crosses below MA50 (momentum fading)
df['Signal'] = 0
df.loc[df['MA20'] > df['MA50'], 'Signal'] = 1    # long
df.loc[df['MA20'] < df['MA50'], 'Signal'] = -1   # short or flat

# --- P&L ---
df['Daily_Return'] = df['Copper'].pct_change()
df['Strategy_Return'] = df['Signal'].shift(1) * df['Daily_Return']
df['Cumulative_Market'] = (1 + df['Daily_Return']).cumprod()
df['Cumulative_Strategy'] = (1 + df['Strategy_Return']).cumprod()

# --- STATS ---
print(df.tail(10))
print(f"\nCurrent signal: {'LONG' if df['Signal'].iloc[-1] == 1 else 'SHORT/FLAT'}")
print(f"MA20: ${df['MA20'].iloc[-1].squeeze():.4f}")
print(f"MA50: ${df['MA50'].iloc[-1].squeeze():.4f}")
print(f"\nStrategy total return: {(df['Cumulative_Strategy'].iloc[-1].squeeze()-1)*100:.2f}%")
print(f"Buy and hold return: {(df['Cumulative_Market'].iloc[-1].squeeze()-1)*100:.2f}%")

# --- PLOT ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

ax1.plot(df.index, df['Copper'], color='steelblue', linewidth=1, label='Copper price')
ax1.plot(df.index, df['MA20'], color='orange', linewidth=1.2, label='MA20')
ax1.plot(df.index, df['MA50'], color='red', linewidth=1.2, label='MA50')
ax1.fill_between(df.index, df['Copper'].min(), df['Copper'].max(),
                  where=(df['Signal'] == 1), alpha=0.1, color='green', label='Long')
ax1.fill_between(df.index, df['Copper'].min(), df['Copper'].max(),
                  where=(df['Signal'] == -1), alpha=0.1, color='red', label='Short')
ax1.set_ylabel('USD/lb')
ax1.set_title('LME Copper — MA20 vs MA50 Signal')
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)

ax2.plot(df.index, df['Cumulative_Strategy'], color='purple', linewidth=1, label='Strategy')
ax2.plot(df.index, df['Cumulative_Market'], color='steelblue', linewidth=1, label='Buy & hold')
ax2.axhline(y=1, color='black', linestyle='--', linewidth=0.8)
ax2.set_ylabel('Growth of $1')
ax2.set_title('Strategy vs Buy & Hold')
ax2.legend(fontsize=8)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('copper_momentum.png')
print("\nChart saved as copper_momentum.png")