"""
Contains code for embedding chunks of text into selected vector databases.
"""
import os
from pathlib import Path
from loguru import logger 
from argparse import ArgumentParser 

from langchain_core.documents import Document
from langchain_chroma.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from src.setup.paths import CHROMA_DIR
from src.setup.config import embed_config
from src.data_processing.cleaning import Cleaner 
from src.data_preparation.sourcing import Author
from src.data_processing.chunking import split_documents 
from src.data_preparation.authors import prepare_sources

    
class ChromaAPI: 
    def __init__(self, author: Author) -> None: 
        self.author: Author = author
        self.embeddings_directory: Path = CHROMA_DIR.joinpath(author.name) 

        # logger.info(f"Creating vector database for {author.name}")
        self.vector_store: Chroma = Chroma(
            collection_name=author.name.replace(" ", "_"),  # Chroma does not permit collection names to have whitespace in them 
            persist_directory=str(self.embeddings_directory),
            embedding_function=get_embedding_model()
        ) 

    def embed_books(self, chunk: bool) -> list[str] | None:

        if len(os.listdir(self.embeddings_directory)) > 1:
            logger.success(f"Embeddings have already been made for {self.author.name}'s texts")
        else:
            cleaner = Cleaner(author=self.author)
            documents: list[Document] | None = cleaner.execute() 
            
            if documents == None:
                raise Exception(f"Unable to retrieve cleaned text for {self.author.name}")
            else:
                logger.info(f"Creating vector embeddings of the texts by {self.author.name}")
                if chunk:
                    chunks: list[Document] = split_documents(documents=documents)
                    ids = self.vector_store.add_documents(documents=chunks)
                else:
                    ids = self.vector_store.add_documents(documents=documents)

                logger.success(f"Successfully embedded the {'chunks of' if chunk else ''} text using ChromaDB.")
                return ids


def get_embedding_model() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=embed_config.embedding_model_name)


if __name__ == "__main__": 

    parser = ArgumentParser()
    _ = parser.add_argument("--chunk", action="store_true")
    args = parser.parse_args()
   
    for author in prepare_sources():
        author.download_books()
        api = ChromaAPI(author=author)
        _ = api.embed_books(chunk=args.chunk)

