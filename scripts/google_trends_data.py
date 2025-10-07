import pandas as pd
from pytrends.request import TrendReq
import time
import os

# Fetch Google Trends for crypto coins using both coin names and symbols with PyTrend library

def fetch_crypto_trends():
    df_crypto = pd.read_csv("./data/crypto_weekly.csv")
    coins = df_crypto[["coin_id", "symbol"]].drop_duplicates().reset_index(drop=True)

    coin_ids = coins["coin_id"].tolist()
    coin_symbols = coins["symbol"].str.lower().tolist()

    pytrends = TrendReq(hl="en-US", tz=360)
    all_trends = pd.DataFrame()

    for i in range(0, len(coin_ids), 5):
        batch_ids = coin_ids[i:i+5]
        batch_symbols = coin_symbols[i:i+5]

        # names
        pytrends.build_payload(batch_ids, cat=0, timeframe="now 7-d", geo="", gprop="")
        df_ids = pytrends.interest_over_time().drop(columns=["isPartial"], errors="ignore")
        time.sleep(5)

        # symbols
        pytrends.build_payload(batch_symbols, cat=0, timeframe="now 7-d", geo="", gprop="")
        df_symbols = pytrends.interest_over_time().drop(columns=["isPartial"], errors="ignore")
        time.sleep(5)

        df_combined = pd.DataFrame(index=df_ids.index)
        for id_col, sym_col in zip(batch_ids, batch_symbols):
            val_id = df_ids.get(id_col, 0)
            val_sym = df_symbols.get(sym_col, 0)
            df_combined[sym_col] = val_id + val_sym

        all_trends = pd.concat([all_trends, df_combined], axis=1)

    all_trends.reset_index(inplace=True)
    all_trends = all_trends.loc[:, ~all_trends.columns.duplicated()]
    return all_trends


if __name__ == "__main__":
    df_trends = fetch_crypto_trends()
    os.makedirs("./data", exist_ok=True)
    save_path = "./data/google_trends_weekly.csv"
    df_trends.to_csv(save_path, index=False)

    print("Saved trends data")
    print(df_trends.head())
