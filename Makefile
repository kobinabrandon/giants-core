books:
	poetry run python src/authors.py

chat:
	poetry run python src/graph/graph.py 


# Embeddings into ChromaDB
embed-chunk:
	poetry run python src/embeddings.py --chunk

embed-no-chunk:
	poetry run python src/embeddings.py 


# Querying Chroma
query-chroma:
	poetry run python src/retrieval/query.py --top_k 10 

generate:
	poetry run python src/generation/main.py --top_p 0 

frontend:
	poetry run streamlit run src/frontend/main.py

