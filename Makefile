.PHONY: setup env data features models clean veryclean

# 0) Create or update the conda environment
setup env:
	conda env update -f environment.yml --prune
	@echo "✅ Environment ready. Activate with: conda activate vol"

# 1) Download and clean data
data:
	python src/data/sp500_list.py
	python src/data/download_yfinance_full.py
	python src/data/clean_prices_csvs.py
	python src/data/assemble_bronze_all.py
	python src/data/download_fred.py
	python src/data/clean_vix.py

# 2) Build features (Gold table)
features:
	python src/features/build_gold_from_csv.py

# 3) Train models
models:
	python src/models/train_rf_xgb.py

# Cleanup options
clean:
	rm -rf data/bronze/* data/gold/*

veryclean:
	rm -rf data/* artifacts/*
	mkdir -p data/raw/prices_by_ticker data/bronze/prices_by_ticker data/gold artifacts
	touch data/.gitkeep

