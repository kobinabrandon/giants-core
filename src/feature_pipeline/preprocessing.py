import re
import json 
import spacy  
import pymupdf
import subprocess
import pandas as pd

from pathlib import Path 

from tqdm import tqdm
from loguru import logger
from pymupdf import Document
from spacy.lang.en import English
from spacy.tokens import Doc, Span

from src.feature_pipeline.data_extraction import neo_colonialism, africa_unite, dark_days, Book

from src.setup.paths import (
    STATISTICS_WITH_SPACY, STATISTICS_WITHOUT_SPACY, PAGE_DETAILS_WITH_SPACY, PAGE_DETAILS_WITHOUT_SPACY,
    make_fundamental_paths
)


class Reader:
    """
    This class is responsible for providing functionality that reads each PDF, and extract information about each page
    that includes but is not limited to: a token count, the number of pages in the document, and the sentences present 
    in each page, and of course how many sentences there are.
    
    In addition to these functions, we can also choose to provide descriptive statistics for all these metrics across 
    pages.
    """
    def __init__(self, book: Book, use_spacy: bool) -> None:
        self.book = book 
        self.use_spacy = use_spacy

    def read_pdf(self) -> Document:
        return pymupdf.open(filename=self.book.file_path)

    @staticmethod
    def remove_newline_marker(text: str) -> str:
        return text.replace("\n", " ").strip()

    def get_page_details(self, document: Document,  describe: bool) -> list[dict] | tuple[list[dict], pd.DataFrame]:
        """
        Extract various details about the book, by collecting these details on a page-by-page basis. 
        For each page, these details will be placed into dictionaries, and then gathered into a list, which
        will then be returned.
        
        Optionally, you can also produce a dataframe of descriptive statistics for the entire book. In this
        case, both the list of page details, and the dataframe of descriptives will be returned. 
        
        Args:
            use_spacy (bool): whether to use spacy to perform sentence segmentation.
            describe (bool): whether to make and save a dataframe containing descriptive statistics for the whole book.
        """
        save_path = PAGE_DETAILS_WITH_SPACY if self.use_spacy else PAGE_DETAILS_WITHOUT_SPACY
        page_details_path = save_path/"all_page_details.json"

        if Path(page_details_path).is_file():
            logger.success(f"The details of every page of {self.book.title} have already been collected -> Fetching them")
            with open(page_details_path) as file:
                all_page_details = json.load(file)
        else:
            all_page_details = []
            for page_number, page in tqdm(
                iterable=enumerate(document),  
                desc=f"Collecting the details of the pages of {self.book.title}"
            ):
                raw_text = page.get_text()
                cleaned_text = self.remove_new_line_(text=raw_text)

                if self.use_spacy:
                    segmenter = SentenceSegmentation(text=cleaned_text, use_spacy=True)
                    tokens = segmenter.get_tokens_with_spacy()
                    sentences = segmenter.segment_with_spacy()   
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
    
        if describe:
            logger.warning("Now to generate descriptive statistics for the details of all the pages")            
            descriptives_path = save_path/f"{self.book.file_name}_descriptives.parquet"
            
            if Path(descriptives_path).is_file():
                logger.success("The descriptives have already been calculated -> Fetching them")
                descriptives = pd.read_parquet(path=descriptives_path)
            else:
                details_dataframe = pd.DataFrame()
                for page_details in tqdm(iterable=all_page_details, desc="Making dataframe of details for each page"):
                    dataframe_of_page = pd.DataFrame(data=page_details)
                    details_dataframe = pd.concat([details_dataframe, dataframe_of_page], axis=0)

                descriptives = details_dataframe.describe().round(2)
                descriptives.to_parquet(descriptives_path)
                return all_page_details, descriptives

        else:        
            return all_page_details


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
    
    def __init__(self, all_page_details: dict) -> None:
        self.all_page_details = all_page_details

    @staticmethod
    def split_sentences(sentences: list[str], split_size: int) -> list[list[str]]:
        """
        Splits a list of sentences into sub-lists, and returns a list that contains these smaller
        lists.

        Args:
            split_size (int): the preferred length of the splits 

        Returns:
            list[list[str]]: the list of lists of sentences
        """
        return [
            sentences[i:i+split_size] for i in range(0, len(self.sentences), split_size)
        ]

    def make_chunks_of_sentences(self, number_of_sentences_per_chunk: int) -> list[dict[str, str|int]]:
        """
        We begin with the list of strings that contains all the sentences. Then we split this list of 
        strings into sublists (the chunks) using the split_sentences method. We also count the number 
        of chunks.
 
        Args:
            number_of_sentences_per_chunk (int): how many sentences we will have in each chunk.

        Returns:
            list[dict[str, str|int]]: the details of each page, which have now been updated with the 
                                      chunks and how many chunks there are in the page.            
        """
        for details_per_page in tqdm(
            iterable=self.all_page_details,
            desc=f"Grouping the sentences in each page into chunks of {number_of_sentences_per_chunk}"
        ):
            details_per_page["sentence_chunk"] = self.split_sentences(
                sentences=details_per_page["sentences"],
                split_size=number_of_sentences_per_chunk
            )

            details_per_page["number_of_chunks"] = len(details_per_page["sentence_chunk"])

        return self.all_page_details

    @staticmethod
    def merge_sentences_in_chunk(sentence_chunk: list[str]) -> str:
        """
        Merge the sentences in each chunk, replace double spaces with single ones, and remove any leading or trailing 
        spaces. After this, we use a regular expression to solve the problem of the newly merged sentences having no
        space between them. The following regular expression will replace that pattern with a new one where there is 
        such as space.
        
        Args:
            sentence_chunk (list[str]): list of sentences that collectively constitute a chunk

        Returns:
            str: the strings in the chunk that have been merged into a single string.
        """
        merged_chunk = "".join(sentence_chunk).replace("  ", " ").strip()           
        merged_chunk = re.sub(pattern=r'\. ([A-Z])', repl=r'. \1', string=merged_chunk)
        return merged_chunk

    def collect_chunk_info(self) -> list[dict[str, str| int]]:
        """
        For each chunk of sentencsa, we begin by merging the sentences in the chunk into a single string.
        Then, we collect various metrics about the newly merged chunk (including itself) and append those 
        details to a list.

        Returns:
            list[dict[str, str | int]]: a list of dictionaries containing merged chunks and their details.
        """
        all_chunk_details = []
        for details_per_page in tqdm(
            iterable=self.all_page_details, 
            desc="Scouring the pages for the details of each chunk of sentences"
        ):

            # The iterable here is a list which contains lists of strings, each of which is a 
            for sentence_chunk in details_per_page["sentence_chunk"]:
                merged_chunk = self.merge_sentences_in_chunk(sentence_chunk=sentence_chunk)

                chunk_details = {}
                chunk_details["merged_chunk"] = merged_chunk
                chunk_details["page_number"] = sentence_chunk["page_number"]
                chunk_details["character_count"] = len(merged_chunk)
                chunk_details["word_count"] = len([word for word in merged_chunk.split(" ")])

                all_chunk_details.append(chunk_details)
        
        return all_chunk_details


def read_books(books: list[Book], use_spacy: bool, describe: bool):

    for book in books:
        reader = Reader(book=book, use_spacy=use_spacy)
        document = reader.read_pdf()
        reader.get_page_details(document=document, describe=describe)


if __name__ == "__main__":
    read_books(
        books=[neo_colonialism, africa_unite, dark_days], use_spacy=True, describe=True
    )