"""
Responsible for providing functionality that reads each PDF, and extract information about each page
that includes but is not limited to: a token count, the number of pages in the document, and the sentences present 
in each page, and of course how many sentences there are.

In addition to these functions, we can also choose to provide descriptive statistics for all these metrics across 
pages.
"""
import json 
import pymupdf
import pandas as pd

from tqdm import tqdm 
from pathlib import Path
from loguru import logger

from src.segmentation import get_tokens_with_spacy, segment_with_spacy, add_spacy_pipeline_component

from general.books import Book 
from general.paths import make_data_directories, set_paths


def read_pdf(book: Book) -> pymupdf.Document:
    """
    Read the contents of the specified book.

    Args:
        book: the book to be read.

    Returns:
        pymupdf.Document: the document
    """
    logger.info(f"Reading '{book.title}'")
    return pymupdf.open(filename=book.file_path)


def merge_books(books: list[Book], from_scratch: bool, general: bool) -> str:
    """
    Extract the raw text for each of the provided books, take the raw strings that constitute their contents,
    merge them together, and return the merged string.

    Args:
        books: a list of book objects

        from_scratch: a boolean that indicates whether or not we will be sourcing the books from within the dataframe
                      folders of the "from_scratch" module
        
        general: a boolean that indicates whether or not we will be sourcing the books from within the dataframe
                      folders of the "general" module

    Returns:
        str: the merged contents of the books 
    """
    make_data_directories(from_scratch=from_scratch, general=general)  # Just to ensure that the directories are present.
    paths = set_paths(from_scratch=from_scratch, general=general) 
    
    CLEANED_TEXT_DIR = paths["cleaned_text"] 

    if len(books) == 1:
        raw_text_file_name = f"raw_text_{[book.file_name for book in books][0]}.txt"
    else:
        raw_text_file_name = "merged_books.txt"

    file_path: Path = CLEANED_TEXT_DIR / raw_text_file_name

    if Path(file_path).is_file():
       logger.success("The file containing the raw text is already present")
       with open(file_path, mode="r") as text_file:
           return text_file.read()
    else:
       logger.warning("There is no file that contains the raw text -> Generating it")
       book_contents: list[str] = []

       for book in books:
           logger.warning(f"Checking for the presence of {book.title}...")
           book.download(upload=False)
          
           intro_page, end_page = book.non_core_pages  
           document = read_pdf(book=book)    
       
           for page_number, page in tqdm(iterable=enumerate(document), desc=f"Extracting the raw text of {book.title}"):
               
               if page_number in range(intro_page, end_page+1):
                   raw_text: str = page.get_text()
                   cleaned_text: str = remove_new_line_marker(text=raw_text)
                   book_contents.append(cleaned_text) 
       
       if len(books) > 1:
           logger.warning("Merging the books into a single string")
        
       else:
           logger.warning(f'Saving the raw text of {[book.title for book in books][0]}')

       merged_text = " ".join(book_contents)
       with open(file_path, mode="w") as text_file:
           _  = text_file.write(merged_text)
       
       return merged_text


def scan_pages_for_details(
    book: Book, 
    document: pymupdf.Document, 
    save_path: Path, 
    use_spacy: bool, 
    describe: bool
    ) -> list[dict[str, str|int]]:
    """
    Extract various details about the book, by collecting these details on a page-by-page basis. 
    For each page, these details will be placed into dictionaries, and then gathered into a list, which
    will then be returned.

    Args:
        book (Book): the Book object to get the details from.
        save_path (Path): the directory where the details are to be saved.
        use_spacy (bool): whether to use spacy to perform sentence segmentation.
        document (pymupdf.Document): the document file obtained from reading the PDF.
        describe (bool): whether we want to save a dataframe containing descriptives statistics 

    Returns:
        list[dict[str, str|int]]: a dictionary of details about each page.
    """
    path_to_book_details = save_path / f"{book.title}_page_details.json"

    if Path(path_to_book_details).is_file():
        logger.success(f'The details of all the pages of {book.title} have been saved -> Fetching them')
        with open(path_to_book_details, mode="r") as file:
            details_of_all_pages: list[dict[str, int|list[str]]] = json.load(file)
    else:
        details_of_all_pages = []
        process_description = f'Collecting details of the pages of "{book.title}"'

        for page_number, page in tqdm(iterable=enumerate(document), desc=process_description):
            raw_text: str = page.get_text()
            cleaned_text = remove_new_line_marker(text=raw_text)

            if use_spacy:
                doc_file = add_spacy_pipeline_component(text=raw_text)
                tokens = get_tokens_with_spacy( doc_file=doc_file)
                sentences = segment_with_spacy(doc_file=doc_file)   
            else:
                tokens = cleaned_text.split(" ")                
                sentences = cleaned_text.split(". ")

            page_details: dict[str, int|list[str]] = {   
                "page_number": page_number,
                "sentences": sentences,
                "character_count_per_page": len(cleaned_text),
                "sentence_count_per_page": len(sentences),   
                "token_count_per_page": len(tokens)
            }

            details_of_all_pages.append(page_details)

        if describe: 
            save_descriptives(book=book, details_of_all_pages=details_of_all_pages, save_path=save_path)

        logger.success(f'Saving the details of all the pages of "{book.title}"')
        with open(path_to_book_details, mode="w") as file:
            json.dump(details_of_all_pages, file)       
      
    return details_of_all_pages


def save_descriptives(book: Book, save_path: Path, details_of_all_pages: list[dict[str, str|int]]) -> None:
    """
    Construct and save a datframe using the details of all the pages of the specific book. 

    Args:
        book: the book whose details are being tabulated. 
        save_path: the path where the dataframe of details is to be saved.
        details_of_all_pages: a list of dictionaries that contains the details of each page.
    """
    descriptives_path = save_path/f"{book.file_name}_descriptives.parquet"    
    
    # Retrieve the descriptives if we already have them
    if Path(descriptives_path).is_file():
        logger.success("The descriptives have already been calculated -> Fetching them")
        descriptives: pd.DataFrame = pd.read_parquet(path=descriptives_path)
    
    else:
        dataframe_of_all_details = pd.DataFrame()
        for page_details in tqdm(iterable=details_of_all_pages, desc="Making dataframe of details for each page"):
            dataframe_of_page_details = pd.DataFrame(data=page_details)
            dataframe_of_all_details = pd.concat([dataframe_of_all_details, dataframe_of_page_details], axis=0)

        descriptives: pd.DataFrame = dataframe_of_all_details.describe().round(2)
        descriptives.to_parquet(descriptives_path)

