import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# Calculate KPIs for each coin and generate visualizations for analysis

IMG_DIR = "analysis_charts"
os.makedirs(IMG_DIR, exist_ok=True)

plt.style.use("ggplot") 
plt.rcParams.update({"figure.dpi": 150, "axes.titlesize": 14, "axes.labelsize": 11})
colors = plt.cm.tab10.colors

# Loading data
df_crypto = pd.read_csv("./data/crypto_weekly.csv")
df_trends = pd.read_csv("./data/google_trends_weekly.csv")

df_crypto["date"] = pd.to_datetime(df_crypto["timestamp"])
df_trends["date"] = pd.to_datetime(df_trends["date"])


# Pivot crypto data
df_crypto["coin_label"] = df_crypto["symbol"].str.lower()
df_crypto_pivot = df_crypto.pivot_table(
    index="date",
    columns="coin_label",
    values="price"
).reset_index()


# Align timestamps
# convert crypto prices to daily average
df_crypto_pivot.set_index("date", inplace=True)
df_crypto_daily = df_crypto_pivot.resample("D").mean().reset_index()

# convert trends data to daily average
df_trends.set_index("date", inplace=True)
df_trends_daily = df_trends.resample("D").mean().reset_index()

# Merge dataframes
df_merged = pd.merge(df_crypto_daily, df_trends_daily, on="date", how="inner")
df_merged.rename(columns=lambda x: x.replace('_x', '_price').replace('_y', '_trend'), inplace=True)


# Create KPIs
coins = [col.replace("_price","") for col in df_merged.columns if col.endswith("_price")]
kpi_list = []

for coin in coins:
    prices = df_merged[f"{coin}_price"].dropna()
    trends = df_merged[f"{coin}_trend"].dropna()

    min_len = min(len(prices), len(trends))
    prices = prices.iloc[:min_len]
    trends = trends.iloc[:min_len]

    weekly_return = (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0] * 100
    volatility = prices.std()
    max_price = prices.max()
    min_price = prices.min()
    avg_trend = trends.mean()
    corr_price_trend = np.corrcoef(prices, trends)[0,1]

    kpi_list.append({
        "coin": coin,
        "weekly_return_%": weekly_return,
        "volatility": volatility,
        "max_price": max_price,
        "min_price": min_price,
        "avg_trends": avg_trend,
        "price_trend_corr": corr_price_trend
    })

df_kpis = pd.DataFrame(kpi_list)
df_kpis.to_csv("./data/crypto_weekly_kpis.csv", index=False)
print("Saved KPI summary")
print(df_kpis)


##################


# Price line charts (subplot)
fig, axes = plt.subplots(len(coins), 1, figsize=(10, 4*len(coins)), sharex=True)
for i, (ax, coin) in enumerate(zip(axes, coins)):
    ax.plot(df_merged["date"], df_merged[f"{coin}_price"],
            label=coin.upper(), color=colors[i % len(colors)], linewidth=2)
    ax.set_ylabel("Price (USD)")
    ax.set_title(coin.upper(), fontsize=12)
    ax.legend(loc="upper left")
plt.xlabel("Date")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "crypto_prices_subplots.png"))
plt.close()

# Trends line chart
plt.figure(figsize=(10,6))
for coin in coins:
    plt.plot(df_merged["date"], df_merged[f"{coin}_trend"], label=coin.upper())
plt.title("Google Trends Interest (Daily Avg)")
plt.xlabel("Date")
plt.ylabel("Trends Index")
plt.legend()
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "google_trends.png"))
plt.close()

# Weekly return bar chart
plt.figure(figsize=(8,5))
sns.barplot(x="coin", y="weekly_return_%", data=df_kpis, palette="Spectral")
plt.title("Weekly Return (%)")
plt.xlabel("Coin")
plt.ylabel("Return (%)")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "weekly_return.png"))
plt.close()

# Volatility strip plot
plt.figure(figsize=(8,5))
sns.stripplot(x="coin", y="volatility", data=df_kpis, size=20)
plt.title("Weekly Volatility (Std Dev)")
plt.xlabel("Coin")
plt.ylabel("Volatility")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "volatility_strip.png"))
plt.close()

# Correlation heatmap (price & trend)
corr_data = []
for coin in coins:
    prices = df_merged[f"{coin}_price"]
    trends = df_merged[f"{coin}_trend"]
    corr_data.append(pd.Series([prices.corr(trends)], index=[coin]))
corr_df = pd.DataFrame(corr_data).T
plt.figure(figsize=(8,6))
sns.heatmap(corr_df, annot=True, fmt=".2f", cmap="vlag",center=0, cbar=True)
plt.title("Correlation: Price vs Google Trends")
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "correlation_price_trend.png"))
plt.close()


# Table visual
df_formatted = df_kpis.copy()
for col in df_formatted.columns:
    if df_formatted[col].dtype in ['float64', 'int64']:
        df_formatted[col] = df_formatted[col].round(1).astype(str).str.upper()
    else:
        df_formatted[col] = df_formatted[col].str.upper()


fig, ax = plt.subplots(figsize=(10, len(df_formatted) * 0.4 + 0.5))  
ax.axis('off')

table = ax.table(cellText=df_formatted.values,
                 colLabels=df_formatted.columns.str.upper(),
                 cellLoc='center',
                 loc='center',
                 bbox=[0, 0, 1, 1])  


table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)  

for col in range(len(df_formatted.columns)):
    table.auto_set_column_width(col=col)
for row in range(len(df_formatted) + 1):  
    table[(row, 0)].set_width(table[(row, 0)].get_width() * 1.5)  

# Set background color
for row in range(len(df_formatted) + 1): 
    for col in range(len(df_formatted.columns)):
        if row == 0:
            table[(row, col)].set_facecolor('#add8e6') 
        else:
            table[(row, col)].set_facecolor('#f0f0f0') 

plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
plt.savefig(os.path.join(IMG_DIR, "kpi_table.png"))
plt.close()
