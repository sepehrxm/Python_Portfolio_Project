import requests
import pandas as pd
import time
import os

# Fetch top 5 cryptocurrencies for the week and their price data throughout the week with CoinGecko api

def get_top5_ids():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 5,
        "page": 1,
        "sparkline": False
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    coins = [{"id": coin["id"], "symbol": coin["symbol"].upper()} for coin in data]
    print("Top 5 coins:", [c["id"] for c in coins])
    return coins


def get_historical_prices(coin_id, symbol):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": 7}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["coin_id"] = coin_id
    df["symbol"] = symbol
    return df


def fetch_top5_historical():
    coins = get_top5_ids()
    all_data = pd.DataFrame()
    for c in coins:
        df = get_historical_prices(c["id"], c["symbol"])
        all_data = pd.concat([all_data, df])
        time.sleep(10)  # prevent rate limiting
    return all_data.reset_index(drop=True)


if __name__ == "__main__":
    df_all = fetch_top5_historical()

    os.makedirs("./data", exist_ok=True)
    save_path = "./data/crypto_weekly.csv"

    df_all.to_csv(save_path, index=False)
    print("Saved crypto data")
    print(df_all.head())
