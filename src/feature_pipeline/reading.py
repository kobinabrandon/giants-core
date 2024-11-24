"""
Responsible for providing functionality that reads each PDF, and extract information about each page
that includes but is not limited to: a token count, the number of pages in the document, and the sentences present 
in each page, and of course how many sentences there are.

In addition to these functions, we can also choose to provide descriptive statistics for all these metrics across 
pages.
"""
import os
import re
import json 
import spacy  
import pymupdf
import pandas as pd

from tqdm import tqdm 
from pathlib import Path
from loguru import logger
from pymupdf import Document

from src.types import SectionDetails, BooksAndDetails
from src.feature_pipeline.data_extraction import Book
from src.feature_pipeline.segmentation import get_tokens_with_spacy, segment_with_spacy, add_spacy_pipeline_component


def read_pdf(book: Book) -> Document:
    return pymupdf.open(filename=book.file_path)


def remove_new_line_marker(text: str) -> str:
    return text.replace("\n", " ").strip()


def scan_page_for_details(book: Book, use_spacy: bool, document: Document, save_path: Path) -> list[SectionDetails]:
    """
    Extract various details about the book, by collecting these details on a page-by-page basis. 
    For each page, these details will be placed into dictionaries, and then gathered into a list, which
    will then be returned.

    Args:
        book (Book): the Book object to get the details from.
        save_path (Path): the directory where the details are to be saved.
        document (Document): the document file obtained from reading the PDF.
        use_spacy (bool): whether to use spacy to perform sentence segmentation.

    Returns:
        list[SectionDetails]:
    """
    page_details_path = save_path/f"{book.title}.json"
    if Path(page_details_path).is_file():
        logger.success(f'The details of all the pages of {book.title} have been saved -> Fetching them')
        with open(page_details_path, mode="r") as file:
            details_of_all_pages = json.load(file)

    else:
        details_of_all_pages = []
        for page_number, page in tqdm(iterable=enumerate(document), desc=f'Collecting details of pages of "{book.title}"'):
            raw_text = page.get_text()
            cleaned_text = remove_new_line_marker(text=raw_text)

            if use_spacy:
                doc_file = add_spacy_pipeline_component(text=raw_text, component_name="sentencizer")
                tokens = get_tokens_with_spacy(text=cleaned_text, doc_file=doc_file)
                sentences = segment_with_spacy(doc_file=doc_file)   
            else:
                tokens = cleaned_text.split(" ")                
                sentences = cleaned_text.split(". ")

            page_details = {   
                "page_number": page_number,
                "sentences": sentences,
                "character_count_per_page": len(cleaned_text),
                "sentence_count_per_page": len(sentences),   
                "token_count_per_page": len(tokens)
            }

            details_of_all_pages.append(page_details)

        logger.success(f'Saving the details of all the pages of "{book.title}"')
        with open(page_details_path, mode="w") as file:
            json.dump(details_of_all_pages, file)       
      
    return details_of_all_pages


def save_descriptives(book: Book, details_of_all_pages: list[SectionDetails], save_path: Path) -> None:

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
