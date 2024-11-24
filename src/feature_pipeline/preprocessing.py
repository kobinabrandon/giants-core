"""

""" 
import pandas as pd 

from tqdm import tqdm
from pathlib import Path 
from loguru import logger
from pymupdf import Document
from argparse import ArgumentParser, BooleanOptionalAction

from src.feature_pipeline.data_extraction import neo_colonialism, africa_unite, dark_days, Book
from src.feature_pipeline.reading import read_pdf, remove_new_line_marker, scan_pages_for_details
from src.feature_pipeline.chunking import make_chunks_of_sentences, merge_sentences_in_chunk, collect_chunk_info

from src.setup.paths import (
    STATS_WITH_SPACY, STATS_WITHOUT_SPACY, PAGE_DETAILS, PAGE_DETAILS_WITH_SPACY, PAGE_DETAILS_WITHOUT_SPACY,
    CHUNK_DETAILS_DIR, make_data_directories
)


def perform_sentence_chunking(book: Book, details_of_all_pages: dict[str, str|int], examine_chunk_details: bool) -> None:
    """
    Produce a dataframe of descriptive statistics for the entire book. In this  case, both the list of page details,
    and the dataframe of descriptives will be returned. 

    Args:
        books (list[Book]): list of book objects 
        details_of_all_pages (dict[str, str|int]):

        book_details (BooksAndDetails): a dictionary whose keys are the titles of the books in question, and each 
                                            of whose values is a list of dictionaries of page details and/or the same 
                                            list which contains either a list of dictionaries (each dictionary of 
                                            those dictionary provides the details of each page)    
    Returns:
        : _description_
    """
    updated_details_for_per_page = make_chunks_of_sentences(
        book_title=book.title, 
        details_of_all_pages=details_of_all_pages
    )
    
    chunk_details = collect_chunk_info(details_of_all_pages=updated_details_for_per_page)
    if examine_chunk_details:
        chunk_details_df = pd.DataFrame(data=chunk_details)
        chunk_details_df.to_parquet(CHUNK_DETAILS_DIR/f"{book.title}.parquet")


if __name__ == "__main__":
    make_data_directories()

    parser = ArgumentParser()
    _ = parser.add_argument("--use_spacy", action=BooleanOptionalAction)
    _ = parser.add_argument("--describe", action=BooleanOptionalAction)

    args = parser.parse_args()
    save_path = PAGE_DETAILS_WITH_SPACY if args.use_spacy else PAGE_DETAILS_WITHOUT_SPACY

    for book in [neo_colonialism, africa_unite, dark_days]:
        document = read_pdf(book=book)

        details_of_all_pages = scan_pages_for_details(
            book=book,
            document=document, 
            save_path=save_path,
            use_spacy=args.use_spacy, 
            describe=args.describe
        )

        chunk_info = perform_sentence_chunking(
            book=book, 
            details_of_all_pages=details_of_all_pages,
            examine_chunk_details=True
        )
