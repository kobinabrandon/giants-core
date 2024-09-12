import spacy  
import pymupdf
import subprocess
import pandas as pd

from tqdm import tqdm
from loguru import logger
from spacy.lang.en import English
from spacy.tokens import Doc, Span

from src.feature_pipeline.data_extraction import neo_colonialism, africa_unite, dark_days, Book

from src.setup.paths import (
    STATISTICS_WITH_SPACY, STATISTICS_WITHOUT_SPACY, PAGE_DETAILS_WITH_SPACY, PAGE_DETAILS_WITHOUT_SPACY
)


class Processor:

    def __init__(self, book: Book, segment_with_spacy: bool) -> None:
        self.book = book
        self.segment_with_spacy = segment_with_spacy

    @staticmethod
    def format_text(text: str):
        return text.replace("\n", " ").strip()

    @staticmethod
    def add_spacy_pipeline_component(text: list[str], component_name: str) -> Doc:

        nlp = English()
        nlp.add_pipe(factory_name=component_name)
        doc_file = nlp(text=text)
        return doc_file

    def get_tokens_with_spacy(self, text: list[str]) -> list[str]:
        doc_file = self.add_spacy_pipeline_component(text=text, component_name="sentencizer")
        return [token.text for token in doc_file if not token.is_space]
    
    def sentence_segmentation_with_spacy(self, text: list[str]) -> list[Span]:

        doc_file = self.add_spacy_pipeline_component(text=text, component_name="sentencizer")
        sentences = list(doc_file.sents)
        return sentences  
            
    def read_pdf(self, describe: bool):
        """
        Read the book, extract various details about the book, collect this information into a dataframe, 
        and return it.

        Args:
            segment_with_spacy (bool): whether to use spacy to perform sentence segmentation.
            describe (bool): whether to make and save a dataframe containing descriptive statistics for 
                             the whole book.
        """
        page_details_and_texts = []
        document = pymupdf.open(filename=self.book.file_path)
        
        for page_number, page in tqdm(
            iterable=enumerate(document), 
            desc=f"Working through the pages of {self.book.title}"
        ):
            
            raw_text = page.get_text()
            cleaned_text = self.format_text(text=raw_text)

            if self.segment_with_spacy:
                tokens = self.get_tokens_with_spacy(text=cleaned_text)
                sentences = self.sentence_segmentation_with_spacy(text=cleaned_text)   
            else:
                tokens = cleaned_text.split(" ")                
                sentences = cleaned_text.split(". ")

            page_details_and_texts.append(
                {
                    "page_number": page_number,
                    "character_count_per_page": len(cleaned_text),
                    "sentences_per_page": len(sentences),   
                    "token_count_per_page": len(tokens), 
                    "text": cleaned_text
                }
            )

        texts_df = pd.DataFrame(data=page_details_and_texts)

        if describe:
            descriptives_df = texts_df.describe().round(2)
            save_path = STATISTICS_WITH_SPACY if self.segment_with_spacy else STATISTICS_WITHOUT_SPACY
            descriptives_df.to_parquet(save_path/f"{self.book.file_name}_descriptive_statistics.parquet")

        else:
            save_path = PAGE_DETAILS_WITH_SPACY if self.segment_with_spacy else PAGE_DETAILS_WITHOUT_SPACY
            texts_df.to_parquet(save_path/f"{self.book.file_name}_page_details.parquet")

    @staticmethod
    def split_list_of_sentences(sentence_list: list, split_size: int) -> list[list[str]]:
        """
        Splits a list of sentences into sub-lists, and returns the a list that contains all 
        these smaller lists.

        Args:
            sentence_list (list): the original list of sentences
            split_size (int): the preferred length of the splits 

        Returns:
            list[list[str]]: the list of lists of sentences
        """
        return [
            sentence_list[i: i+slice_size] for i in range(0, len(sentence_list), split_size)
        ]


def process_all_books(books: list[Book], segment_with_spacy: bool, describe: bool):

    for book in books:
        processor = Processor(book=book, segment_with_spacy=segment_with_spacy)
        processor.read_pdf(describe=describe)


if __name__ == "__main__":
    process_all_books(
        books=[neo_colonialism, africa_unite, dark_days], segment_with_spacy=True, describe=True
    )