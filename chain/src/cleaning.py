"""
Contains code that cleans text using by interacting with object's of Langchain's Document class.
"""
from langchain_core.documents import Document
from general.cleaning import remove_new_line_marker


def remove_non_core_pages(documents: list[Document], core_pages: range) -> list[Document]:
    """
    Scan all the Document objects in a given book, and remove those that come from most pages tat are not core
    to the book in question.

    Args:
        documents: list of Document objects representing the information of each page of a given book
        core_pages: a range of integers representing the page numbers of all the core pages of the book.

    Returns:
       list[Document]: list of Document objects that contain the information of the core pages of the book. 
    """
    for _ in range(3):  # For some reason, running the inner loop once isn't removing all the qualified pages. 
        for document in documents:
            metadata: dict[str, str | int] = document.metadata
            if metadata["page"] not in core_pages: 
                documents.remove(document)

    return documents 


def remove_new_line_from_documents(documents: list[Document]) -> list[Document]:
    """
    Look at the text contained in each Document object, remove the new line markers inside these texts, and 
    put those cleaner texts back into that Document object.
    
    Args:
        documents: Document objects whose text is to be cleaned up a bit. 

    Returns:
        list[Document]: the list of all the Document objects with cleaner text. 
    """
    for document in documents:
        document.page_content = remove_new_line_marker(text=document.page_content)
    
    return documents

