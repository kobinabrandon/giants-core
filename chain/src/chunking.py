from loguru import logger
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.config import config

from general.books import Book
from general.reading import merge_books


def split_text_into_chunks(books: list[Book]) -> list[str]:

    text = merge_books(books=books, from_scratch=False, general=False)

    splitter = RecursiveCharacterTextSplitter(
       chunk_size=config.chunk_size,
       chunk_overlap=config.chunk_overlap,
       length_function=config.length_function,
       add_start_index=config.add_start_index
    )
    
    chunks = splitter.split_text(text=text)
    logger.success(f"Split the combined text of our books into {len(chunks)} chunks")     
    return chunks

