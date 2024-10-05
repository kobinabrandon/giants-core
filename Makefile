books:
	poetry run python src/feature_pipeline/data_extraction.py

process:
	poetry run python src/feature_pipeline/preprocessing.py
	