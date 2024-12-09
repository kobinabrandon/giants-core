import torch

from loguru import logger 
from time import perf_counter as timer 
from sentence_transformers import util, SentenceTransformer

from src.feature_pipeline import embeddings
from src.feature_pipeline.embeddings import get_embedding_model, retrieve_embeddings_of_chunks
from src.feature_pipeline.data_extraction import Book, neo_colonialism, dark_days, africa_unite


def perform_dot_product(query: str, book: Book) -> torch.Tensor: 
    
    logger.info(f"Query: {query}")
    embedding_model: SentenceTransformer = get_embedding_model()
    query_embedding = embedding_model.encode(query, convert_to_tensor=True)
    
    text_embeddings = retrieve_embeddings_of_chunks(book=book) 
    breakpoint()

    start_time = timer()
    dot_product_score = util.dot_score(a=query_embedding, b=text_embeddings)
    end_time = timer()

    logger.success(f"Time taken to get scores on {len(text_embeddings)} embeddings: {end_time-start_time:.5f} seconds.") 
    
    top_results = torch.topk(dot_product_score, k=5)
    breakpoint()
    return top_results 


perform_dot_product(query="What is Neocolonialism?", book=neo_colonialism)


