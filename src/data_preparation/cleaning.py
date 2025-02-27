"""
Contains code that cleans the raw text in the documents of a given book
"""
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

from src.data_preparation.sourcing import Book


def clean_books(books: list[Book]) -> list[Document]:
    """
    Loads each book using Langchain's PDF loader, resulting in a list of instances of Langchain's Document
    class. It then cleans the pages of each book by performing the following cleaning tasks. 
        - removing pages that aren't core to the text
        - removing new line markers
        - removing specified artifacts
        - rewriting words that were not properly scanned by the reader.

    Args:
        books: a list of Books to be read and processed.

    Returns:
        list[Document]: list of Document objects containing the cleaned contents of each page from each book.
    """
    loader_list: list[Document] = []
    for book in books:
        loader = PyPDFLoader(file_path=str(book.file_path))
        documents: list[Document] = loader.load()
        main_pages: list[Document] = remove_non_core_pages(documents=documents, book=book) 
        documents_without_new_lines: list[Document] = remove_new_line_markers(documents=main_pages)
        
        for document in documents_without_new_lines:
            if "the" in document.page_content:
                # breakpoint()
                document.page_content = fix_known_spelling_issues(text=document.page_content)
        
        loader_list.extend(documents_without_new_lines)

    return loader_list 


def remove_non_core_pages(documents: list[Document], book: Book) -> list[Document]:
    """
    Scan all the Document objects in a given book, and remove those that come from most pages that are not core
    to the book in question.

    Args:
        documents: list of Document objects representing the information of each page of a given book
        book: the book whose text we are cleaning

    Returns:
       list[Document]: list of Document objects that contain the information of the core pages of the book. 
    """
     
    if book.core_pages != None:
        # For some reason, running the inner loop once isn't removing all the qualified pages. 
        for document in documents:
            metadata: dict[str, str | int] = document.metadata
            if metadata["page"] not in book.core_pages: 
                documents.remove(document)

    return documents 


def fix_known_spelling_issues(text: str) -> str:
    """
    Replace a target string with a preferred one.

    Args:
        text: the text to be searched for the target string

    Returns:
       str: the string following all the changes. 
    """
    target_strings_and_replacements = {
        r"\xad": "", 
        "19 66": "1966",
        "I 966": "1966",
        "Cl.A": "C.I.A",
        r"\'coup\'": "coup",
        "fkunkeys": "flunkeys" 
    }

    for target_string in target_strings_and_replacements.keys():
        replacement = target_strings_and_replacements[target_string]
        text = text.replace(target_string, replacement)

    return text 


def remove_new_line_markers(documents: list[Document]) -> list[Document]:
    """
    Look at the text contained in each Document object, remove the new line markers inside these texts, and 
    put those cleaner texts back into that Document object.
    
    Args:
        documents: Document objects whose text is to be cleaned up a bit. 

    Returns:
        list[Document]: the list of all the Document objects with cleaner text. 
    """
    for document in documents:
        raw_text = document.page_content
        document.page_content = raw_text.replace("\n", " ").strip()

    return documents

