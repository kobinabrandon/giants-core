from langchain_core.documents import Document 
from langchain_community.document_loaders import PyPDFLoader

from general.books import Book, neo_colonialism
from general.cleaning import remove_new_line_marker


def read_books(books: list[Book]) -> list[Document]:

    loader_list: list[Document] = []
    for book in books:
        book.download()
        loader = PyPDFLoader(file_path=str(book.file_path))

        document_per_page: list[Document] = loader.load()
        document_per_core_page = remove_non_core_pages(documents=document_per_page, core_pages=book.core_pages)  
        documents_without_new_lines = remove_new_line_from_documents(documents=document_per_core_page)

        loader_list.extend(documents_without_new_lines)

    return loader_list 


def remove_non_core_pages(documents: list[Document], core_pages: range) -> list[Document]:
    
    for _ in range(3):  # For some reason, running the inner loop once isn't removing all the qualified pages. 
        for document in documents:
            metadata: dict[str, str | int] = document.metadata
            if metadata["page"] not in core_pages: 
                documents.remove(document)

    return documents 


def remove_new_line_from_documents(documents: list[Document]) -> list[Document]:

    for document in documents:
        document.page_content = remove_new_line_marker(text=document.page_content)
    
    return documents

