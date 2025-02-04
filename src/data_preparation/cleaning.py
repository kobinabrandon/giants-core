"""
Contains code that cleans the raw text in the documents of a given book
"""
from langchain_core.documents import Document


def clean_book(documents: list[Document], book_file_name: str) -> list[Document]:
    """
    This function cleans the pages of the given book by performing the following tasks:
        - removing pages that aren't core to the text
        - removing new line markers
        - removing specified artifacts
        - rewriting words that were not properly scanned by the reader.

    Args:
        documents: Document objects representing each page of the book
        book_file_name: the name of the PDF representation of the book

    Returns:
        list[Document]: Document objects that represent the cleaned pages. 
    """
    core_pages= remove_non_core_pages(documents=documents, book_file_name=book_file_name)
    cleaner_pages: list[Document] = remove_new_line_markers(documents=core_pages)
    
    target_strings_and_replacements = {
        r"\xad": "", 
        "Cl.A": "C.I.A",
        "fkunkeys": "flunkeys", 
        r"\'coup\'": "coup",
        "19 66": "1966",
        "I 966": "1966"
    }

    for document in cleaner_pages:
        if "the" in document.page_content:
            # breakpoint()
            document.page_content = fix_known_spelling_issues(
                text=document.page_content, 
                target_strings_and_replacements=target_strings_and_replacements
            )

            # breakpoint()

    return cleaner_pages


def remove_non_core_pages(documents: list[Document], book_file_name: str) -> list[Document]:
    """
    Scan all the Document objects in a given book, and remove those that come from most pages that are not core
    to the book in question.

    Args:
        documents: list of Document objects representing the information of each page of a given book
        core_pages: a range of integers representing the page numbers of all the core pages of the book.

    Returns:
       list[Document]: list of Document objects that contain the information of the core pages of the book. 
    """

    book_and_core_pages: dict[str, range] = {
        "neo_colonialism": range(4, 202),
        "africa_must_unite": range(5, 237),
        "dark_days": range(7, 163)
    }

    assert book_file_name in book_and_core_pages.keys()
    core_pages = book_and_core_pages[book_file_name]

    for _ in range(3):  # For some reason, running the inner loop once isn't removing all the qualified pages. 
        for document in documents:
            metadata: dict[str, str | int] = document.metadata
            if metadata["page"] not in core_pages: 
                documents.remove(document)

    return documents 


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


def fix_known_spelling_issues(text: str, target_strings_and_replacements: dict[str, str]) -> str:
    """
    Replace a target string with a preferred one.

    Args:
        text: the text to be searched for the target string
        target_strings_and_replacements: a dictionary consisting of strings and their intending replacements 

    Returns:
       str: the string following all the changes. 
    """
    for target_string in target_strings_and_replacements.keys():
        replacement = target_strings_and_replacements[target_string]
        text = text.replace(target_string, replacement)

    return text 

