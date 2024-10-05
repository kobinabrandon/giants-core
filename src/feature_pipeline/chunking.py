"""
Contains functions that group sentences into chunks.
"""
import re
from src.types import PageDetails, BooksAndDetails


def make_chunks_of_sentences(all_page_details: dict, sentences_per_chunk: int) -> List[PageDetails]:
    """
    We begin with the list of strings that contains all the sentences. Then we split this list of 
    strings into sublists (the chunks) using the split_sentences method. We also count the number 
    of chunks.

    Args:
        sentences_per_chunk (int): how many sentences we will have in each chunk.

    Returns:
        list[dict[str, str|int]]: the details of each page, which have now been updated with the 
                                    chunks and how many chunks there are in the page.            
    """
    for details_per_page in tqdm(
        iterable=all_page_details,
        desc=f"Grouping the sentences in each page into chunks of {sentences_per_chunk}"
    ):
        details_per_page["sentence_chunk"] = split_sentences(
            sentences=details_per_page["sentences"],
            split_size=sentences_per_chunk
        )

        details_per_page["number_of_chunks"] = len(details_per_page["sentence_chunk"])

    return all_page_details


def collect_chunk_info(all_page_details: dict) -> list[dict[str, str| int]]:
    """
    For each chunk of sentencsa, we begin by merging the sentences in the chunk into a single string.
    Then, we collect various metrics about the newly merged chunk (including itself) and append those 
    details to a list.

    Returns:
        list[dict[str, str | int]]: a list of dictionaries containing merged chunks and their details.
    """
    all_chunk_details = []
    for details_per_page in tqdm(
        iterable=all_page_details, 
        desc="Scouring the pages for the details of each chunk of sentences"
    ):

        # The iterable here is a list which contains lists of strings, each of which is a 
        for sentence_chunk in details_per_page["sentence_chunk"]:
            merged_chunk = merge_sentences_in_chunk(sentence_chunk=sentence_chunk)

            chunk_details = {}
            chunk_details["merged_chunk"] = merged_chunk
            chunk_details["page_number"] = sentence_chunk["page_number"]
            chunk_details["character_count"] = len(merged_chunk)
            chunk_details["word_count"] = len([word for word in merged_chunk.split(" ")])

            all_chunk_details.append(chunk_details)
    
    return all_chunk_details


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


def split_sentences(sentences: list[str], split_size: int) -> list[list[str]]:
    """
    Splits a list of sentences into sub-lists, and returns a list that contains these smaller
    lists.

    Args:
        split_size (int): the preferred length of the splits 

    Returns:
        list[list[str]]: a list of sub-lists of sentences
    """
    return [
        sentences[i:i+split_size] for i in range(0, len(sentences), split_size)
    ]
