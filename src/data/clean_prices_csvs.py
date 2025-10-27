import os, glob
import pandas as pd
from pathlib import Path

RAW = "data/raw/prices_by_ticker"
BRONZE = "data/bronze/prices_by_ticker"
Path(BRONZE).mkdir(parents=True, exist_ok=True)

NUM_COLS = ["open","high","low","close","adj_close","volume"]

def clean_one(path: str) -> tuple[str, int]:
    tkr = Path(path).stem.upper()

    df = pd.read_csv(path, dtype=str, header=0)

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    if "adj_close" not in df.columns:
        for c in df.columns:
            if c.replace(" ", "") in {"adjclose", "adj_close"}:
                df = df.rename(columns={c: "adj_close"})
                break

    df = df.loc[:, ~df.columns.str.startswith("unnamed")]

    df["date"] = pd.to_datetime(df.get("date"), errors="coerce")

    for c in NUM_COLS:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    if "ticker" not in df.columns:
        df["ticker"] = tkr
    else:
        df["ticker"] = df["ticker"].astype(str).str.strip().str.upper().fillna(tkr)

    df = df.dropna(subset=["date"])
    if any(c in df.columns for c in NUM_COLS):
        df = df.dropna(subset=[c for c in NUM_COLS if c in df.columns], how="all")

    keep = ["date","open","high","low","close","adj_close","volume","ticker"]
    df = df[[c for c in keep if c in df.columns]].copy()

    df = df.drop_duplicates(subset=["ticker","date"]).sort_values("date")

    if "volume" in df.columns:
        df = df[df["volume"].isna() | (df["volume"] >= 0)]

    outp = f"{BRONZE}/{tkr}.csv"
    df.to_csv(outp, index=False)
    return tkr, len(df)

def main():
    files = sorted(glob.glob(f"{RAW}/*.csv"))
    ok, fail = 0, 0
    for i, f in enumerate(files, 1):
        try:
            t, n = clean_one(f)
            ok += 1
            if i % 25 == 0:
                print(f"[{i}/{len(files)}] cleaned {t}: {n} rows")
        except Exception as e:
            fail += 1
            print(f"{os.path.basename(f)} -> {e}")
    print(f"Done. Cleaned={ok}, Failed={fail}. Output → {BRONZE}/")

if __name__ == "__main__":
    main()
