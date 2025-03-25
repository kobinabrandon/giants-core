books:
	uv run src/authors.py

manage:
	uv run src/data_preparation/management.py

archive:
	uv run src/data_preparation/archive.py

ocr:
	uv run src/data_preparation/ocr.py

read:
	uv run src/data_processing/reading.py

embed-chunk:
	uv run src/data_processing/embeddings.py --chunk

embed-no-chunk:
	uv run src/data_processing/embeddings.py 

generate:
	uv run src/generation.py

chat:
	uv run src/graph/graph.py 

