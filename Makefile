# Downloading raw data 
books:
	poetry run python src/books.py


# Indexing with Pinecone
pinecone-multi:
	poetry run python src/embeddings.py --multi_index

pinecone-single:
	poetry run python src/embeddings.py --no-multi_index


# Embeddings with ChromaDB
chroma-chunk:
	poetry run python src/embeddings.py --chroma --chunk

chroma-no-chunk:
	poetry run python src/embeddings.py --chroma 


# Querying Chroma
query-chroma:
	poetry run python src/retrieval.py --chroma --top_k 10 


# Quering Pinecone 
query-single-index:
	poetry run python src/retrieval.py --top_k 10 

query-dark-days:
	poetry run python src/retrieval.py --multi_index --book_file_name dark_days --top_k 10 

query-africa-unite:
	poetry run python src/retrieval.py --multi_index --book_file_name africa_unite --top_k 10 

query-neocolonialism:
	poetry run python src/retrieval.py --multi_index --book_file_name neo_colonialism --top_k 10


# Generation 
generate:
	poetry run python src/generation.py --task text_generation 

# qa:
# 	poetry run python src/generation.py --request_type client --method qa 

# generate_no_open_ai:
# 	poetry run python src/generation.py --request_type client --method generation

# generate_open_ai:
# 	poetry run python src/generation.py --request_type client --method generation --use_open_ai

