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

from src.types import PageDetails, BooksAndDetails
from src.feature_pipeline.data_extraction import Book
from src.feature_pipeline.segmentation import get_tokens_with_spacy, segment_with_spacy, add_spacy_pipeline_component


from src.setup.paths import (
    STATS_WITH_SPACY, STATS_WITHOUT_SPACY, PAGE_DETAILS, PAGE_DETAILS_WITH_SPACY, PAGE_DETAILS_WITHOUT_SPACY,
    make_fundamental_paths
)


def read_pdf(book: Book) -> Document:
    return pymupdf.open(filename=book.file_path)


def remove_new_line_marker(text: str) -> str:
    return text.replace("\n", " ").strip()


def get_page_details(book: Book, use_spacy: bool, document: Document, describe: bool) -> List[PageDetails]:
    """
    Extract various details about the book, by collecting these details on a page-by-page basis. 
    For each page, these details will be placed into dictionaries, and then gathered into a list, which
    will then be returned.
    
    Optionally, you can also produce a dataframe of descriptive statistics for the entire book. In this
    case, both the list of page details, and the dataframe of descriptives will be returned. 

    Args:
        book (Book): the Book object to get the details from.
        document (Document): the document file obtained from reading the PDF.
        use_spacy (bool): whether to use spacy to perform sentence segmentation.
        describe (bool): whether to make and save a dataframe containing descriptive statistics for the whole book.

    Returns:
        List[PageDetails]:
    """
    save_path = PAGE_DETAILS_WITH_SPACY if use_spacy else PAGE_DETAILS_WITHOUT_SPACY
    page_details_path = save_path/"all_page_details.json"
    make_fundamental_paths()

    if Path(page_details_path).is_file():
        logger.success(f"The details of every page of {book.title} have already been collected -> Fetching them")
        with open(page_details_path) as file:
            all_page_details = json.load(file)
    else:
        all_page_details = []
        for page_number, page in tqdm(
            iterable=enumerate(document),  
            desc=f'Collecting the details of the pages of "{book.title}"'
        ):
            raw_text = page.get_text()
            cleaned_text = remove_new_line_marker(text=raw_text)

            if use_spacy:
                doc_file = add_spacy_pipeline_component(text=raw_text, component_name="sentencizer")
                tokens = get_tokens_with_spacy(text=raw_text, doc_file=doc_file)
                sentences = segment_with_spacy(text=raw_text, doc_file=doc_file)   
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

            all_page_details.append(page_details)

        logger.success(f'Saving the details of all the pages of "{book.title}"')
        with open(save_path/f"{book.title}.json", mode="w") as file:
            json.dump(all_page_details, file)

    if describe:
        logger.warning("Now generating descriptive statistics for the details of all the pages")            
        descriptives_path = save_path/f"{book.file_name}_descriptives.parquet"
        
        if Path(descriptives_path).is_file():
            logger.success("The descriptives have already been calculated -> Fetching them")
            descriptives = pd.read_parquet(path=descriptives_path)
        else:
            dataframe_of_all_details = pd.DataFrame()
            for page_details in tqdm(iterable=all_page_details, desc="Making dataframe of details for each page"):
                dataframe_of_page_details = pd.DataFrame(data=page_details)
                dataframe_of_all_details = pd.concat([dataframe_of_all_details, dataframe_of_page_details], axis=0)

            descriptives = dataframe_of_all_details.describe().round(2)
            descriptives.to_parquet(descriptives_path)
      
    return all_page_details
