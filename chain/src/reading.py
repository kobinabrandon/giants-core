from langchain_core.documents import Document 
from langchain.document_loaders import PyPDFLoader, PyPDFDirectoryLoader 
from general.books import neo_colonialism, Book 


def read_pdf(book: Book) -> list[Document]:

    loader = PyPDFDirectoryLoader(path=book.file_path.parent.resolve())
    breakpoint()
    return loader.load()


read_pdf(book=neo_colonialism)
