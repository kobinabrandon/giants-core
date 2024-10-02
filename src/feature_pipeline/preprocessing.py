import spacy  
import pymupdf
import subprocess
import pandas as pd

from pathlib import Path 

from tqdm import tqdm
from loguru import logger
from spacy.lang.en import English
from spacy.tokens import Doc, Span
from pymupdf import Document

from src.feature_pipeline.data_extraction import neo_colonialism, africa_unite, dark_days, Book

from src.setup.paths import (
    STATISTICS_WITH_SPACY, STATISTICS_WITHOUT_SPACY, PAGE_DETAILS_WITH_SPACY, PAGE_DETAILS_WITHOUT_SPACY,
    make_fundamental_paths
)


class Reader:
    def __init__(self, book: Book, use_spacy: bool) -> None:
        self.book = book 
        self.use_spacy = use_spacy

    def read_pdf(self) -> Document:
        return pymupdf.open(filename=self.book.file_path)
    
    def get_page_details(self, document: Document,  describe: bool) -> list[dict] | pd.DataFrame:
        """
        Extract various details about the book, collect this information into a dataframe, 
        and return it.

        Args:
            use_spacy (bool): whether to use spacy to perform sentence segmentation.
            describe (bool): whether to make and save a dataframe containing descriptive statistics for the whole book.
        """
        page_details = []
        for page_number, page in tqdm(
            iterable=enumerate(document),  
            desc=f"Working through the pages of {self.book.title}"
        ):

            raw_text = page.get_text()
            cleaned_text = format_text(text=raw_text)

            if self.use_spacy:
                segmenter = SentenceSegmentation(text=cleaned_text, use_spacy=True)
                tokens = segmenter.get_tokens_with_spacy()
                sentences = segmenter.segment_with_spacy()   
            else:
                tokens = cleaned_text.split(" ")                
                sentences = cleaned_text.split(". ")

            page_details.append(
                {   
                    "page_number": page_number,
                    "sentences": sentences,
                    "character_count_per_page": len(cleaned_text),
                    "sentence_count_per_page": len(sentences),   
                    "token_count_per_page": len(tokens)
                }
            )

        if describe:
            logger.warning(
                f'To produce descriptive statistics for each document, we will create a dataframe of details\
                for each page called "{self.book.file_name}_page_details", and use that to produce the descriptives.'
            )

            details_dataframe = pd.DataFrame()
            for details_dict in tqdm(iterable=page_details, desc="Making dataframe of details for each page"):
                details_dataframe = pd.concat([details_dataframe, details_dict], axis=0)
            
            save_path = PAGE_DETAILS_WITH_SPACY if self.use_spacy else PAGE_DETAILS_WITHOUT_SPACY
            details_dataframe.to_parquet(save_path/f"{self.book.file_name}_page_details.parquet")

            descriptives = details_dataframe.describe().round(2)
            descriptives.to_parquet(save_path/f"{self.book.file_name}_descriptives.parquet")
            return descriptives

        else:        
            return page_details_and_texts


class SentenceSegmentation:
    def __init__(self, text: list[str], use_spacy: bool) -> None:
        self.text = text    
        self.use_spacy = use_spacy

    def segment_with_spacy(self) -> list[Span]:
        doc_file = self.add_spacy_pipeline_component(component_name="sentencizer")
        sentences = list(doc_file.sents)
        return sentences  

    def add_spacy_pipeline_component(self, component_name: str) -> Doc:

        nlp = English()
        nlp.add_pipe(factory_name=component_name)
        doc_file = nlp(text=self.text)
        return doc_file

    def get_tokens_with_spacy(self) -> list[str]:
        doc_file = self.add_spacy_pipeline_component(component_name="sentencizer")
        return [token.text for token in doc_file if not token.is_space]

    
    
class SentenceChunking:
    
    def __init__(self, sentences: list[str]) -> None:
        self.sentences = sentences
    
    def split_list_of_sentences(self, split_size: int) -> list[list[str]]:
        """
        Splits a list of sentences into sub-lists, and returns a list that contains these s,aller
        lists.

        Args:
            split_size (int): the preferred length of the splits 

        Returns:
            list[list[str]]: the list of lists of sentences
        """
        return [
            self.sentences[i:i+split_size] for i in range(0, len(self.sentences), split_size)
        ]

    def make_chunks_of_sentences(self, number_of_sentences_per_chunk: int, page_details: dict) -> dict[str, str|int]:
        
        for page_detail in tqdm(
            iterable=page_details,
            desc=f"Grouping the sentences in each page into chunks of {number_of_sentences_per_chunk}"
        ):
            page_detail["sentence_chunks"] = self.split_list_of_sentences(split_size=number_of_sentences_per_chunk)
            page_detail["number_of_chunks"] = len(page_detail["sentence_chunks"])

        return page_details





def format_text(text: str) -> str:
    return text.replace("\n", " ").strip()


def process_all_books(books: list[Book], use_spacy: bool, describe: bool):

    for book in books:
        reader = Reader(book=book, use_spacy=use_spacy)
        document = reader.read_pdf()
        reader.get_page_details(document=document, describe=describe)


if __name__ == "__main__":
    process_all_books(
        books=[neo_colonialism, africa_unite, dark_days], use_spacy=True, describe=True
    )