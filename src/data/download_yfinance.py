import os, time, yaml, math
import pandas as pd
import yfinance as yf

cfg = yaml.safe_load(open("conf/data.yml"))
paths = yaml.safe_load(open("conf/paths.yml"))

RAW_DIR = paths["raw_dir"]
os.makedirs(f"{RAW_DIR}/prices_by_ticker", exist_ok=True)

sp = pd.read_csv(cfg["sp500_list_csv"])
tickers = sp["ticker"].dropna().unique().tolist()

start, end = cfg["start"], cfg["end"]

def dl_one(t):
    try:
        df = yf.download(t, start=start, end=end, interval="1d",
                         auto_adjust=False, progress=False, threads=False)
        if df.empty:
            return None
        df = df.reset_index().rename(columns=str.lower)
        df["ticker"] = t
        return df
    except Exception:
        return None

vix = dl_one(cfg["vix_ticker"])
if vix is not None:
    vix.to_csv(f"{RAW_DIR}/vix.csv", index=False)
    print("Saved VIX:", vix.shape)

skipped, saved, failed = 0, 0, 0
for i, t in enumerate(tickers, 1):
    outp = f"{RAW_DIR}/prices_by_ticker/{t}.csv"
    if os.path.exists(outp):
        skipped += 1
        continue
    df = dl_one(t)
    if df is None or df.empty:
        failed += 1
    else:
        df.to_csv(outp, index=False)
        saved += 1
    if i % 25 == 0:
        print(f"[{i}/{len(tickers)}] saved={saved} skipped={skipped} failed={failed}")
    time.sleep(0.35)

print(f"DONE | saved={saved} skipped={skipped} failed={failed} of {len(tickers)}")
