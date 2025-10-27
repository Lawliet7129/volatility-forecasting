import pandas as pd
import os

RAW_PATH = "data/raw/vix.csv"
CLEAN_PATH = "data/bronze/vix.csv"

os.makedirs("data/bronze", exist_ok=True)

def main():
    df = pd.read_csv(RAW_PATH)

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    df = df.dropna(subset=["date"])

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    keep = ["date", "adj_close", "close", "high", "low", "open", "volume"]
    df = df[keep]

    df["ticker"] = "VIX"

    df = df.drop_duplicates(subset="date")

    print(df.head())
    print(f"Cleaned VIX → {len(df):,} rows")

    df.to_csv(CLEAN_PATH, index=False)

if __name__ == "__main__":
    main()
