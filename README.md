# 🧠 Volatility Forecasting for S&P 500 Constituents

### 🎯 Objective
Predict **next-day realized volatility** for each S&P 500 stock using historical prices, VIX levels, and macroeconomic indicators (FRED).  
This project is built in Python and follows a reproducible data pipeline (`raw → bronze → gold`).


## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/volatility-forecasting.git
cd volatility-forecasting
```

### 2. Create Conda Environment
```bash
conda env create -f environment.yml
conda activate vol
```
If the environment already exists:
```bash
make setup
```


### IMPORTANT: All large data files stay local (ignored by Git).
Data Pipeline: To fully rebuild the dataset on your machine:
```bash
make data
```
This runs:
- src/data/sp500_list.py → fetch S&P 500 tickers
- src/data/download_yfinance_full.py → download Yahoo Finance OHLCV data
- src/data/clean_prices_csvs.py → clean and normalize
- src/data/assemble_bronze_all.py → combine all tickers into a single dataset
- src/data/download_fred.py → fetch FRED macro series (e.g., FEDFUNDS, CPI)
- src/data/clean_vix.py → clean VIX index data
