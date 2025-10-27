import os, yaml
import pandas as pd
from pandas_datareader import data as pdr

cfg = yaml.safe_load(open("conf/data.yml"))
paths = yaml.safe_load(open("conf/paths.yml"))
os.makedirs(paths["raw_dir"], exist_ok=True)

start, end = cfg["start"], cfg["end"]
series = cfg["fred_series"]

dfs = []
for s in series:
    s_df = pdr.DataReader(s, "fred", start=start, end=end).rename(columns={s: "value"})
    s_df["series"] = s
    s_df = s_df.reset_index().rename(columns={"DATE":"date"})
    dfs.append(s_df)

fred = pd.concat(dfs, ignore_index=True)
fred.to_csv(f'{paths["raw_dir"]}/fred.csv', index=False)
print("FRED rows:", len(fred))
