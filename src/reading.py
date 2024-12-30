"""
Provides code that reads text and prepares it for chunking.
"""
from langchain_core.documents import Document 
from langchain_community.document_loaders import PyPDFLoader

from src.books import Book
from src.cleaning import remove_non_core_pages, remove_new_line_from_documents


def read_books(books: list[Book]) -> list[Document]:
    """
    Loads each book using Langchain's PDF loader, resulting in a list of instances of Langchain's Document
    class. The function then removes pages that aren't core to the text. It also removes the new line 
    markers that are littered throughout the contents of each page.

    Args:
        books: a list of Books to be read and processed.

    Returns:
        list[Document]: list of Document objects containing the cleaned contents of each page from each book.
    """
    loader_list: list[Document] = []
    for book in books:
        book.download()
        loader = PyPDFLoader(file_path=str(book.file_path))

        documents_per_page: list[Document] = loader.load()
        documents_per_core_page: list[Document] = remove_non_core_pages(documents=documents_per_page, core_pages=book.core_pages)  
        documents_without_new_lines: list[Document] = remove_new_line_from_documents(documents=documents_per_core_page)

        loader_list.extend(documents_without_new_lines)

    return loader_list 

