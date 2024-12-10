books:
	poetry run python feature_pipeline/data_extraction.py

process:
	poetry run python feature_pipeline/preprocessing.py --use_spacy --describe

tokens:
	poetry run python feature_pipeline/tokenizer.py

embeddings:
	poetry run python feature_pipeline/embeddings.py 


search:
	poetry run python feature_pipeline/semantic_search.py 
