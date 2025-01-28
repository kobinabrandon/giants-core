from loguru import logger
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer    
from transformers import AutoTokenizer, PreTrainedTokenizer
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.setup.config import chunk_config, embed_config 
from src.data_preparation.books import read_and_clean_books, neo_colonialism, africa_unite, dark_days


def split_documents(documents: list[Document]) -> list[Document]:
    """
    Split the texts (supplied in Langchain's Document format) into chunks using either the 
    number of characters or the number of tokens. The latter choice will be made if there is 
    at least one page whose tokens exceed the maximum sequence length of the embedding model.
    
    Args:
        documents: the documents to be split into chunks 

    Returns:
        list[Document]: the resulting chunks of text
    """
    separators = [r"\n\n", r"\n", ".", " "]
    max_seq_length = get_max_sequence_length()

    if some_pages_too_big_for_embedding(max_seq_length=max_seq_length, documents=documents):
        
        logger.warning("Splitting into chunks by the token")

        splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
            tokenizer=get_tokenizer(), 
            chunk_size=max_seq_length,
            chunk_overlap=int(max_seq_length * chunk_config.ratio_of_tokens_in_overlap),
            add_start_index=True,
            separators=separators
        )

    else:
        logger.warning("Splitting into chunks by the character")

        splitter = RecursiveCharacterTextSplitter(
           chunk_size=chunk_config.number_of_characters_per_chunk,
           chunk_overlap=chunk_config.overlapping_characters_per_chunk,
           length_function=chunk_config.length_function,
           add_start_index=chunk_config.add_start_index,
           separators=separators
        )

       
    chunks: list[Document] = splitter.split_documents(documents=documents)
    logger.success(f"Successfully split the combined text of our books into {len(chunks)} chunks")     
    return chunks


def get_max_sequence_length(embedding_model_name: str = embed_config.embedding_model_name) -> int:
    """
    Determine the maximum sequence length of the embedding model and return it 
    
    Args:
        embedding_model_name: the name of the embedding model.
    Returns:
        int: the maximum number of tokens that the embedding model can handle.
    """
    embedding_model = SentenceTransformer(model_name_or_path=embedding_model_name)
    max_seq_length = embedding_model.max_seq_length
    logger.warning(f"The embedding model has a maximum sequence length of {max_seq_length}")     
    return max_seq_length


def some_pages_too_big_for_embedding(max_seq_length: int, documents: list[Document]) -> bool:
    """
    Uses the embedding model to tokenize the pages of each text, counts the number of tokens, and checks whether any 
    of the pages has more tokens than the embedding model can handle.

    Args:
        max_seq_length: the maximum number of tokens that can be accommodated by the embedding model. 
        documents: the number of documents to be processed.

    Returns:
        bool: whether or not there is a page with more tokens than the embedding model's capacity.
    """
    tokenizer = get_tokenizer() 
    lengths = [len(tokenizer.encode(document.page_content)) for document in documents]
    lengths_beyond_max = [length for length in lengths if length > max_seq_length]
    
    if len(lengths_beyond_max) > 0: 
        logger.warning("There is at least one page whose tokens exceed the max sequence length of the embedding model") 
        return True
    else:
        logger.warning("The number of tokens in each page is less than the max sequence length of the embedding model")
        return False 


def get_tokenizer(name: str = embed_config.embedding_model_name) -> PreTrainedTokenizer:
    return AutoTokenizer.from_pretrained(pretrained_model_name_or_path=name)


if __name__ == "__main__":
    documents = read_and_clean_books(books=[neo_colonialism, africa_unite, dark_days])
    chunks = split_documents(documents=documents)

