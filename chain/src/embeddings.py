from pathlib import Path
from loguru import logger 

from langchain.vectorstores.chroma import Chroma
from langchain.embeddings.huggingface import HuggingFaceEmbeddings 
from langchain.llms.huggingface_pipeline import HuggingFacePipeline 

from src.config import config 
from src.reading import get_text
from src.chunking import split_text_into_chunks

from general.paths import set_paths
from general.books import neo_colonialism, africa_unite, dark_days


def get_model_path():
    paths = set_paths(from_scratch=False, general=False)
    return paths["chroma"]
    

def choose_embedding_model() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=config.sentence_transformer_name)


def set_vector_database(chunks_of_text: list[str] | None, path: Path, embedding_model: HuggingFaceEmbeddings) -> Chroma:
    
    if chunks_of_text is None:
        return Chroma.from_texts(embedding=embedding_model, persist_directory=str(path))
    else:
        return Chroma.from_texts(texts=chunks_of_text, embedding=embedding_model, persist_directory=str(path))


def save_chunks_to_chroma(chunks_of_text: list[str], path: Path) -> None:
    
    embedding_model = choose_embedding_model()
    db = set_vector_database(chunks_of_text=chunks_of_text, path=get_model_path(), embedding_model=embedding_model) 
    db.persist()

    logger.success(f"Saved {len(chunks_of_text)} chunks to {path}")    


def query_embeddings(query: str):
    
    embedding_model = choose_embedding_model()
    db = set_vector_database(chunks_of_text=chunks_of_text, path=get_model_path(), embedding_model=embedding_model) 
    results = db.similarity_search_with_relevance_scores(query=query) 
    


if __name__ == "__main__":
    books = [neo_colonialism, africa_unite, dark_days] 
    text = get_text(books=books) 
    chunks = split_text_into_chunks(books=books)
    save_chunks_to_chroma(chunks_of_text=chunks)

