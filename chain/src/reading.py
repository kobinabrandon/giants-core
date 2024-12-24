from langchain_core.documents import Document 
from langchain.document_loaders import PyPDFLoader, PyPDFDirectoryLoader 

from general.books import Book 
from general.paths import set_paths


def read_text(book: Book | None) -> list[Document]:
    
    module_paths = set_paths(from_scratch=False, general=False)
    books_root = module_paths["raw_data"]

    if book == None: 
        loader = PyPDFDirectoryLoader(path=books_root)    
    else:
        loader = PyPDFLoader(file_path=book.file_path)

    return loader.load()

