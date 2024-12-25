from langchain_core.documents import Document 
from langchain.document_loaders import PyPDFLoader

from general.books import Book 
from general.paths import set_paths


def read_books(books: list[Book]) -> list[Document]:

    loader_list = []
    for book in books:
        book.download()
        loader = PyPDFLoader(file_path=str(book.file_path))
        loader_list.extend(loader.load())

    return loader_list 

