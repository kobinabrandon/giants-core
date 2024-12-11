from tomllib import load
import requests
from pathlib import Path

from loguru import logger

from langchain.document_loaders.pdf import PyPDFDirectoryLoader

from general.paths import make_data_directories
from general.books import Book, africa_unite, neo_colonialism, dark_days



def load_book(book: Book):
    document_loader = PyPDFDirectoryLoader(path=book.file_path)
    return document_loader.load()


make_data_directories(from_scratch=False, general=False)
loaded_text = load_book(book=dark_days)
breakpoint()
