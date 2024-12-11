import requests
from pathlib import Path
from loguru import logger
from paths import RAW_DATA_DIR, make_data_directories
from langchain.document_loaders.pdf import PyPDFDirectoryLoader



def load_book(book: Book):
    document_loader = PyPDFDirectoryLoader(book.file_path)
    return document_loader.load()


