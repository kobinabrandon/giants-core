books:
	poetry run python src/authors.py

manage:
	poetry run python src/data_preparation/management.py

archive:
	poetry run python src/data_preparation/archive.py

ocr:
	poetry run python src/data_preparation/ocr.py

read:
	poetry run python src/data_processing/reading.py

embed-chunk:
	poetry run python src/vector_store/embeddings.py --chunk

embed-no-chunk:
	poetry run python src/vector_store/embeddings.py 


# Querying Chroma
query:
	poetry run python src/retrieval.py --nickname fidel --question "What are the goals of imperialism?" 


chat:
	poetry run python src/graph/graph.py 

# generate:
# 	poetry run python src/generation/main.py --top_p 0 

