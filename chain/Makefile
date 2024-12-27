chunks:
	poetry run python src/chunking.py

generate:
	poetry run python src/generation.py

pinecone-multi:
	poetry run python src/vector_db.py --multi_index

pinecone-single:
	poetry run python src/vector_db.py --no-multi_index

chroma-chunk:
	poetry run python src/vector_db.py --chroma --chunk

chroma-no-chunk:
	poetry run python src/vector_db.py --chroma 

query-chroma:
	poetry run python src/similarity_search.py --chroma --top_k 10 

query-single-index:
	poetry run python src/similarity_search.py --top_k 10 

query-dark-days:
	poetry run python src/similarity_search.py --multi_index --book_file_name dark_days --top_k 10 

query-africa-unite:
	poetry run python src/similarity_search.py --multi_index --book_file_name africa_unite --top_k 10 

query-neocolonialism:
	poetry run python src/similarity_search.py --multi_index --book_file_name neo_colonialism --top_k 10

