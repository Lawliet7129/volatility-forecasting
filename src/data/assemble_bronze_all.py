import pandas as pd
import glob
import os
from pathlib import Path

BRONZE_DIR = Path("data/bronze/prices_by_ticker")
OUT_PATH   = Path("data/bronze/prices_all.csv")

def main():
    files = sorted(glob.glob(str(BRONZE_DIR / "*.csv")))
    if not files:
        raise FileNotFoundError(f"No CSVs found in {BRONZE_DIR}")

    dfs = []
    for i, f in enumerate(files, 1):
        try:
            df = pd.read_csv(f, parse_dates=["date"])
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
            if "ticker" not in df.columns:
                df["ticker"] = os.path.splitext(os.path.basename(f))[0].upper()
            dfs.append(df)

            if i % 25 == 0:
                print(f"[{i}/{len(files)}] processed {os.path.basename(f)}")

        except Exception as e:
            print(f"⚠️  {os.path.basename(f)} -> {e}")

    big = pd.concat(dfs, ignore_index=True)

    big = big.drop_duplicates(subset=["ticker", "date"])
    big = big.sort_values(["ticker", "date"]).reset_index(drop=True)

    for c in ["open", "high", "low", "close", "adj_close", "volume"]:
        if c in big.columns:
            big[c] = pd.to_numeric(big[c], errors="coerce")

    print("Combined:", len(files), "tickers →", len(big), "rows")
    big.to_csv(OUT_PATH, index=False)
    print("Saved:", OUT_PATH)

if __name__ == "__main__":
    main()
