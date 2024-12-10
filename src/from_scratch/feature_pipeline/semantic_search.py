import torch

from loguru import logger 
from time import perf_counter as timer 
from sentence_transformers import util, SentenceTransformer

from feature_pipeline.embeddings import get_embedding_model, retrieve_embeddings_of_chunks
from feature_pipeline.data_extraction import Book, neo_colonialism, dark_days, africa_unite


def perform_dot_product(query: str, book: Book) -> torch.Tensor: 
    
    logger.info(f"Query: {query}")
    embedding_model: SentenceTransformer = get_embedding_model()
    query_embedding = embedding_model.encode(query, convert_to_tensor=True)
    
    print(f"Query embedding shape: {query_embedding.shape}")
    print("\n")

    text_embeddings = retrieve_embeddings_of_chunks(book=book) 
    print(f"Text embedding shape: {text_embeddings.shape}")
    print("\n")
    
    breakpoint()

    start_time = timer()
    dot_product_score = util.dot_score(a=query_embedding, b=text_embeddings)[0]
    end_time = timer()

    logger.success(f"Time taken to get scores on {len(text_embeddings)} embeddings: {end_time-start_time:.5f} seconds.") 
    breakpoint()
    return torch.topk(dot_product_score, k=5)


perform_dot_product(query="What is Neocolonialism?", book=neo_colonialism)

