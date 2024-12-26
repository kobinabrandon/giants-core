from langchain_core.documents import Document 
from langchain_community.document_loaders import PyPDFLoader

from general.books import Book, neo_colonialism
from general.paths import set_paths
from general.cleaning import remove_new_line_marker


def read_books(books: list[Book]) -> list[Document]:

    loader_list = []
    for book in books:
        book.download()
        loader = PyPDFLoader(file_path=str(book.file_path))
        
        breakpoint()

        loader_list.extend(loader.load())
    
    


    return loader_list 


read_books([neo_colonialism])
