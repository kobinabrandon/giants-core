import time 
from loguru import logger 

from pinecone import Pinecone, ServerlessSpec
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone.vectorstores import PineconeVectorStore
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline 

from src.config import config 
from src.chunking import split_text_into_chunks

from general.books import Book, neo_colonialism, africa_unite, dark_days
 

def choose_embedding_model() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=config.sentence_transformer_name)


def create_serverless_pinecone_index(
    cloud: str = "aws", 
    region: str = "us-east-1", 
    metric: str = "cosine"
    ) -> None: 
    """
    The free tier of Pinecone only comes with AWS, and only the "us-east-1" region
    """
    pinecone = Pinecone(api=config.pinecone_api_key)
    spec = ServerlessSpec(cloud=cloud, region=region)
    pinecone.create_index(name=config.pinecone_index, dimension=config.vector_dim, metric=metric, spec=spec)
    
    while not pinecone.describe_index(name=config.pinecone_index).status["ready"]:
        time.sleep(1)


def push_vectors(chunks_of_text: list[str] | None, embedding_model: HuggingFaceEmbeddings) -> PineconeVectorStore:
    
    if chunks_of_text is None:
        return PineconeVectorStore.from_texts(embedding=embedding_model, index_name=config.pinecone_index)
    else:
        return PineconeVectorStore.from_texts(texts=chunks_of_text, embedding=embedding_model, index_name=config.pinecone_index)
    

def query_embeddings(books: list[Book]):
    
    chunks_of_text = split_text_into_chunks(books=books)
    breakpoint()
    embedding_model = choose_embedding_model()

    db = push_vectors(chunks_of_text=chunks_of_text, embedding_model=embedding_model) 
    results = db.similarity_search_with_relevance_scores(query=query) 
    
    if len(results) == 0:
        logger.error("Could not find matching results")
    
