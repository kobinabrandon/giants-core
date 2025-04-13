books:
	uv run src/data_preparation/authors.py

manage:
	uv run src/data_preparation/management.py

archive:
	uv run src/data_preparation/archive.py

ocr:
	uv run src/data_preparation/ocr.py

read:
	uv run src/data_processing/reading.py

embed-chunk:
	uv run src/vector_store/embeddings.py --chunk

embed-no-chunk:
	uv run src/vector_store/embeddings.py 


# Querying Chroma
query:
	uv run src/retrieval.py --nickname rumi --question "What are Rumi's views on God?" 


chat:
	uv run src/graph/graph.py 

# generate:
# 	uv run  src/generation/main.py --top_p 0 

