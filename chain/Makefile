multi-index:
	poetry run python src/indexing.py --multi_index

single-index:
	poetry run python src/indexing.py --no-multi_index

query-single-index:
	poetry run python src/semantic_search.py --no-multi_index --top_k 10 

query-dark-days:
	poetry run python src/semantic_search.py --multi_index --book_file_name dark_days --top_k 10 

query-africa-unite:
	poetry run python src/semantic_search.py --multi_index --book_file_name africa_unite --top_k 10 

query-neocolonialism:
	poetry run python src/semantic_search.py --multi_index --book_file_name neo_colonialism --top_k 10

