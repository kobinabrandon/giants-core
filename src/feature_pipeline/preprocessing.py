"""

""" 
import pandas as pd 

from tqdm import tqdm
from pathlib import Path 
from loguru import logger
from pymupdf import Document
from argparse import ArgumentParser, BooleanOptionalAction

from src.types import SectionDetails, BooksAndDetails
from src.feature_pipeline.data_extraction import neo_colonialism, africa_unite, dark_days, Book
from src.feature_pipeline.reading import read_pdf, remove_new_line_marker, scan_page_for_details, save_descriptives
from src.feature_pipeline.chunking import make_chunks_of_sentences, merge_sentences_in_chunk, collect_chunk_info

from src.setup.paths import (
    STATS_WITH_SPACY, STATS_WITHOUT_SPACY, PAGE_DETAILS, PAGE_DETAILS_WITH_SPACY, PAGE_DETAILS_WITHOUT_SPACY,
    make_fundamental_paths
)


def scan_book_for_details(book: Book, use_spacy: bool, describe: bool) -> BooksAndDetails:
    """
    Read each of the books and produce the lists that contain all the dictionaries that contain the details of each page.

    Args:
        books (list[Book]): the books to be read
        use_spacy (bool): whether to use spacy to perform sentence segmentation 
        describe (bool): whether to produce dataframes of descriptive statistics

    Returns:
        BooksAndDetails: a dictionary whose key is the title of the book in question, and whose value is a list of 
                        dictionaries, each of which provides the details for a specific page.
    """ 
    save_path = PAGE_DETAILS_WITH_SPACY if use_spacy else PAGE_DETAILS_WITHOUT_SPACY
    page_details_path = save_path/"details_of_all_pages.json"

    if Path(page_details_path).is_file():
        logger.success(f"The details of every page of {book.title} have already been collected -> Fetching them")
        with open(page_details_path) as file:
            details_of_all_pages = json.load(file)
    else:
        document = read_pdf(book=book)
        details_of_all_pages = scan_page_for_details(book=book, document=document, use_spacy=use_spacy, save_path=save_path)

        if describe: 
            save_descriptives(book=book, details_of_all_pages=details_of_all_pages, save_path=save_path)

    return details_of_all_pages


def perform_sentence_chunking(book: Book, book_details: BooksAndDetails):
    """
    Produce a dataframe of descriptive statistics for the entire book. In this  case, both the list of page details,
    and the dataframe of descriptives will be returned. 

    Args:
        books (list[Book]): list of book objects 
        book_details (BooksAndDetails): a dictionary whose keys are the titles of the books in question, and each 
                                            of whose values is a list of dictionaries of page details and/or the same 
                                            list which contains either a list of dictionaries (each dictionary of 
                                            those dictionary provides the details of each page)    
    Returns:
        : _description_
    """
    books_and_chunk_info = {}
    details_of_all_pages = book_details[book.title]
    
    updated_details_for_all_pages = make_chunks_of_sentences(
        book_title=book.title, 
        details_of_all_pages=details_of_all_pages
    )
    
    chunk_info = collect_chunk_info(details_of_all_pages=details_of_all_pages)
    books_and_chunk_info[book.title] = chunk_info
        
    return books_and_chunk_info


if __name__ == "__main__":
    make_fundamental_paths()

    parser = ArgumentParser()
    _ = parser.add_argument("--use_spacy", action=BooleanOptionalAction)
    _ = parser.add_argument("--describe", action=BooleanOptionalAction)

    args = parser.parse_args()
    for book in [neo_colonialism, africa_unite, dark_days]:
        book_details = scan_book_for_details(book=book, use_spacy=args.use_spacy, describe=args.describe)
        chunk_info = perform_sentence_chunking(book=book, book_details=book_details)

        df = pd.DataFrame(chunk_info)
        breakpoint()
    
