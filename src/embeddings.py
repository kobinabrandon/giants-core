"""
Contains code for embedding chunks of text into selected vector databases.
"""
import time 
from pathlib import Path
from loguru import logger 
from argparse import ArgumentParser 

from langchain_core.documents import Document
from langchain_chroma.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from src.setup.paths import set_paths
from src.setup.config import embed_config, env_config
from src.data_preparation.cleaning import clean_books
from src.data_preparation.chunking import split_documents 
from src.data_preparation.books import Book
    

class ChromaAPI: 
    def __init__(self) -> None: 
        # self.books: list[Book] = 
        self.embeddings_directory: Path = set_paths()["text_embeddings"] 
        self.memory_directory: Path = set_paths()["chroma_memory"]

        self.main_store: Chroma = Chroma(
            collection_name="nkrumah", 
            persist_directory=str(self.embeddings_directory),
            embedding_function=get_embedding_model()
        ) 

    def embed_books(self, chunk: bool) -> list[str]:

        documents: list[Document] = clean_books(books=self.books)         

        if chunk:
            chunks = split_documents(documents=documents)
            ids = self.main_store.add_documents(documents=chunks)
        else:
            ids = self.main_store.add_documents(documents=documents)

        logger.success(f"Successfully embedded the {'chunks of' if chunk else ''} text and saved the results to ChromaDB.")
        return ids

    def embed_memory(self, text: str) -> list[str]:
        ids: list[str] = self.store.add_texts([text]) 
        logger.success(f"Successfully embedded the memory and saved it to ChromaDB.")
        return ids


def get_embedding_model() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=embed_config.embedding_model_name)


if __name__ == "__main__": 

    parser = ArgumentParser()
    _ = parser.add_argument("--chunk", action="store_true")
    args = parser.parse_args()
   
    api = ChromaAPI()
    ids = api.embed_books(chunk=args.chunk)

