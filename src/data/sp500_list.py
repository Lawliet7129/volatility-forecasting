# src/data/sp500_list.py
import os, re, time
import pandas as pd
import requests

WIKI_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
GITHUB_FALLBACK = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
SNAPSHOT = "conf/sp500_snapshot.csv"

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def _fix_ticker(t: str) -> str:
    # BRK.B -> BRK-B, BF.B -> BF-B, strip spaces
    t = str(t).strip().replace(".", "-")
    return re.sub(r"\s+", "", t)

def from_wikipedia() -> pd.DataFrame:
    resp = requests.get(WIKI_URL, headers=UA, timeout=20)
    resp.raise_for_status()
    tables = pd.read_html(resp.text)   # parse from the fetched HTML
    df = tables[0]                     # first table = constituents
    df = df.rename(columns={
        "Symbol": "ticker",
        "GICS Sector": "sector",
        "GICS Sub-Industry": "sub_industry",
        "Security": "security"
    })
    df["ticker"] = df["ticker"].map(_fix_ticker)
    return df[["ticker","sector","sub_industry","security"]]

def from_github_fallback() -> pd.DataFrame:
    df = pd.read_csv(GITHUB_FALLBACK)
    # some mirrors use different headers; normalize
    cols = {c.lower(): c for c in df.columns}
    sym_col = cols.get("symbol") or cols.get("ticker") or list(df.columns)[0]
    name_col = cols.get("name") or cols.get("security") or list(df.columns)[1]
    sec_col  = cols.get("sector", None)

    out = pd.DataFrame({
        "ticker": df[sym_col].map(_fix_ticker),
        "security": df[name_col],
        "sector": df[sec_col] if sec_col in df.columns else "Unknown",
        "sub_industry": "Unknown"
    })
    return out[["ticker","sector","sub_industry","security"]]

def load_sp500_snapshot(path=SNAPSHOT) -> pd.DataFrame:
    if os.path.exists(path):
        try:
            snap = pd.read_csv(path)
            if {"ticker","sector"}.issubset(snap.columns) and len(snap) > 0:
                return snap
        except Exception:
            pass
    # Try Wikipedia with UA; then fallback; then raise
    try:
        df = from_wikipedia()
        print(f"[info] Pulled {len(df)} tickers from Wikipedia.")
    except Exception as e:
        print(f"[warn] Wikipedia fetch failed ({e}). Using fallback source…")
        df = from_github_fallback()
        print(f"[info] Pulled {len(df)} tickers from fallback.")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"[info] Saved snapshot -> {path}")
    return df

if __name__ == "__main__":
    df = load_sp500_snapshot(SNAPSHOT)
    print(df.head())
    print(f"Total tickers: {len(df)}")
