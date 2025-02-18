books:
	poetry run python src/data_preparation/books.py

chat:
	poetry run python src/graph/graph.py 


# Embed into Pinecone
pinecone-multi:
	poetry run python src/embeddings.py --multi_index

pinecone-single:
	poetry run python src/embeddings.py --no-multi_index


# Embeddings into ChromaDB
chroma-chunk:
	poetry run python src/embeddings.py --chroma --chunk

chroma-no-chunk:
	poetry run python src/embeddings.py --chroma 


# Querying Chroma
query-chroma:
	poetry run python src/retrieval/query.py --chroma --top_k 10 


# Quering Pinecone 
query-single-index:
	poetry run python src/retrieval/query.py --top_k 10 

query-dark-days:
	poetry run python src/query.py --multi_index --book_file_name dark_days --top_k 10 

query-africa-unite:
	poetry run python src/query.py --multi_index --book_file_name africa_unite --top_k 10 

query-neocolonialism:
	poetry run python src/query.py --multi_index --book_file_name neo_colonialism --top_k 10


generate:
	poetry run python src/generation/main.py --top_p 0 


frontend:
	poetry run streamlit run src/frontend/main.py


#
# qa:
# 	poetry run python src/experimental_generation.py request_type client --method qa 
#
# generate_no_open_ai:
# 	poetry run python src/experimental_generation.py request_type client --method generation
#
# generate_open_ai:
# 	poetry run python src/experimental_generation.py request_type client --method generation --use_open_ai

