from loguru import logger
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.config import config
from general.books import Book

from src.reading import read_books


def split_text_into_chunks(books: list[Book]) -> list[Document]:
    
    documents = read_books(books=books)

    splitter = RecursiveCharacterTextSplitter(
       chunk_size=config.chunk_size,
       chunk_overlap=config.chunk_overlap,
       length_function=config.length_function,
       add_start_index=config.add_start_index,
       separators=["\n\n", "\n", ".", " "]
    )

    chunks = splitter.split_documents(documents=documents)
    logger.success(f"Split the combined text of our books into {len(chunks)} chunks")     
    return chunks

