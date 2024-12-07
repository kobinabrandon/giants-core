"""
Contains functions that group sentences into chunks.
"""
from pathlib import Path
import re
import pandas as pd 
import sentencepiece as spm

from tqdm import tqdm

from src.setup.config import config 
from src.setup.types import SectionDetails
from src.setup.paths import CHUNK_DETAILS_DIR, MODELS_DIR
from src.feature_pipeline.data_extraction import Book
from src.feature_pipeline.reading import remove_new_line_marker


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
    updated_details_for_per_page = make_chunks_of_sentences(book_title=book.title, details_of_all_pages=details_of_all_pages)
    chunk_details = collect_chunk_info(book=book, details_of_all_pages=updated_details_for_per_page)

    if examine_chunk_details:
        chunk_details_df = pd.DataFrame(data=chunk_details)
        chunk_details_df.to_parquet(CHUNK_DETAILS_DIR/f"{book.title}.parquet")


def make_chunks_of_sentences(
    book_title: str, 
    details_of_all_pages: list[dict[str, str|int]], 
    sentences_per_chunk: int = 30
    ) -> list[dict[str, str|int]]:
    """
    Taking the list of dictionaries which contains the all the details of the page that were collected, we extract the
    list of strings that contains all the sentences.Then we split this list of strings into sublists (the chunks) using 
    the split_sentences method. We also count the number of chunks.

    Args:
        book_title (str):
        details_of_all_pages (list[dict[str, str|int]]): 
        sentences_per_chunk (int): how many sentences we will have in each chunk.

    Returns:
        list[dict[str, str|int]]: the details of each page, which have now been updated with the chunks and how many
                            chunks there are in the page.            
    """
    for details_per_page in tqdm(
        iterable=details_of_all_pages, 
        desc=f'Grouping the sentences in each page of "{book_title}" into chunks of {sentences_per_chunk}'
    ):
        sentences_of_the_page: list[str]= details_per_page["sentences"]
        details_per_page["chunks_of_sentences"] = split_sentences(sentences=sentences_of_the_page, split_size=sentences_per_chunk)
        details_per_page["number_of_chunks"] = len(details_per_page["chunks_of_sentences"])

    return details_of_all_pages


def collect_chunk_info(book: Book, details_of_all_pages: list[dict[str, str|int]]) -> list[SectionDetails]:
    """
    For each chunk of sentencsa, we begin by merging the sentences in the chunk into a single string.
    Then, we collect various metrics about the newly merged chunk (including itself) and append those 
    details to a list.

    Returns:
        list[dict[str, str | int]]: a list of dictionaries containing merged chunks and their details.
    """
    all_chunk_details = []
    for details_per_page in tqdm(iterable=details_of_all_pages, desc="Scouring the pages for the details of each chunk of sentences"):
       
        # The iterable here is a list which contains lists of strings, each of which is a 
        for sentence_chunk in details_per_page["chunks_of_sentences"]:

            chunk_details = {}
            merged_chunk: str = merge_sentences(sentence_chunk=sentence_chunk)
            merged_chunk: str = remove_new_line_marker(text=merged_chunk)
            
            tokenizer_path = train_tokenizer(book=book, chunk=merged_chunk)
            tokens = tokenize_chunk(chunk=merged_chunk, model_path=tokenizer_path)

            chunk_details["merged_chunk"] = merged_chunk
            chunk_details["page_number"] = details_per_page["page_number"]
            chunk_details["chunk_character_count"] = len(merged_chunk)
            chunk_details["chunk_word_count"] = len([word for word in merged_chunk.split(" ")])
            chunk_details["chunk_tokens"] = tokens 
            chunk_details["chunk_token_count"] = len(tokens)

            all_chunk_details.append(chunk_details)
            
            breakpoint()

    return all_chunk_details


def merge_sentences(sentence_chunk: list[str]) -> str:
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


def split_sentences(sentences: list[str], split_size: int) -> list[list[str]]:
    """
    Splits a list of sentences into sub-lists, and returns a list that contains these smaller
    lists.

    Args:
        split_size (int): the preferred length of the splits 
        sentences (list[str]): 

    Returns:
        list[list[str]]: a list of sub-lists of sentences
    """
    return [
        sentences[i:i+split_size] for i in range(0, len(sentences), split_size)
    ]


def train_tokenizer(book: Book, chunk: str) -> str:
    
    spm.SentencePieceTrainer.Train(
       sentence_iterator=iter(chunk), 
       model_prefix=f"{book.file_name}_spm_model", 
       pad_id=config.pad_id,
       unk_id=config.unk_id,
       bos_id=config.bos_id,
       eos_id=config.eos_id,
       vocab_size=46
    )
    
    return f"{book.file_name}_spm_model"


def tokenize_chunk(chunk: str, model_path: tuple[Path]) -> str:
    
    processor = spm.SentencePieceProcessor(model_file=model_path)
    return processor.Encode(chunk, out_type=str)
    
