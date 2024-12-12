from dataclasses import dataclass
from loguru import logger 

from langchain.vectorstores.chroma import Chroma
from langchain.embeddings.ollama import OllamaEmbeddings

from src.reading import get_text
from src.chunking import split_text_into_chunks

from general.paths import set_paths
from general.books import neo_colonialism, africa_unite, dark_days


def save_chunks_to_chroma(chunks_of_text: list[str]) -> None:
    
    paths = set_paths(from_scratch=False, general=False)
    CHROMA_DIR = paths["chroma"]

    db = Chroma.from_texts(
            texts=chunks_of_text,
            embedding=OllamaEmbeddings(model="llama3"),
            persist_directory=str(CHROMA_DIR)
        )

    db.persist()
    logger.success(f"Saved {len(chunks_of_text)} chunks to {CHROMA_DIR}")    


if __name__ == "__main__":
    books = [neo_colonialism, africa_unite, dark_days] 
    text = get_text(books=books) 
    chunks = split_text_into_chunks(books=books)
    save_chunks_to_chroma(chunks_of_text=chunks)

