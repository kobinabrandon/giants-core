from loguru import logger
from transformers import AutoTokenizer
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer    
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.config import config
from src.reading import read_books
from general.books import neo_colonialism, africa_unite, dark_days


def split_documents(documents: list[Document]) -> list[Document]:
    
    separators = ["\n\n", "\n", ".", " "]
    max_seq_length = get_max_sequence_length()

    if some_pages_too_big_for_embedding(max_seq_length=max_seq_length, documents=documents):
        
        logger.warning("Splitting into chunks by the token")

        splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
            tokenizer=get_tokenizer(), 
            chunk_size=max_seq_length,
            chunk_overlap=int(max_seq_length * config.ratio_of_tokens_in_overlap),
            add_start_index=True,
            separators=separators
        )

    else:

        logger.warning("Splitting into chunks by the character")

        splitter = RecursiveCharacterTextSplitter(
           chunk_size=config.number_of_characters_per_chunk,
           chunk_overlap=config.overlapping_characters_per_chunk,
           length_function=config.length_function,
           add_start_index=config.add_start_index,
           separators=separators
        )

       
    chunks: list[Document] = splitter.split_documents(documents=documents)
    logger.success(f"Split the combined text of our books into {len(chunks)} chunks")     
    return chunks


def get_max_sequence_length(embedding_model_name: str = config.embedding_model_name) -> int:
    
    embedding_model = SentenceTransformer(model_name_or_path=embedding_model_name)
    max_seq_length = embedding_model.max_seq_length
    logger.warning(f"The embedding model has a maximum sequence length of {max_seq_length}")     
    return max_seq_length


def some_pages_too_big_for_embedding(max_seq_length: int, documents: list[Document]) -> bool:

    tokenizer = get_tokenizer() 
    lengths = [len(tokenizer.encode(document.page_content)) for document in documents]
    lengths_beyond_max = [length for length in lengths if length > max_seq_length]
    
    if len(lengths_beyond_max) > 0: 
        logger.warning("There is at least one page whose tokens exceed the max sequence length of the embedding model") 
        return True
    else:
        logger.warning("The number of tokens in each page is less than the max sequence length of the embedding model")
        return False 


def get_tokenizer(name: str = config.embedding_model_name):
    return AutoTokenizer.from_pretrained(pretrained_model_name_or_path=name)



if __name__ == "__main__":
    documents = read_books(books=[neo_colonialism, africa_unite, dark_days])
    chunks = split_documents(documents=documents)
    breakpoint()
