books:
	poetry run python src/authors.py

selection:
	poetry run python src/data_preparation/management.py

archive:
	poetry run python src/data_preparation/archive.py

ocr:
	poetry run python src/data_preparation/ocr.py

read:
	poetry run python src/data_processing/reading.py




# chat:
# 	poetry run python src/graph/graph.py 
#
#
# # Embeddings into ChromaDB
# embed-chunk:
# 	poetry run python src/embeddings.py --chunk
#
# embed-no-chunk:
# 	poetry run python src/embeddings.py 
#
#
# # Querying Chroma
# query-chroma:
# 	poetry run python src/retrieval/query.py --top_k 10 
#
# generate:
# 	poetry run python src/generation/main.py --top_p 0 
#
# frontend:
# 	poetry run streamlit run src/frontend/main.py

