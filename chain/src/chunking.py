from loguru import logger
from transformers import AutoTokenizer
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer    
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.config import config
from src.reading import read_books
from general.books import neo_colonialism, africa_unite, dark_days


def split_documents_into_chunks(documents: list[Document]) -> list[Document]:
    
    splitter = RecursiveCharacterTextSplitter(
       chunk_size=config.chunk_size,
       chunk_overlap=config.chunk_overlap,
       length_function=config.length_function,
       add_start_index=config.add_start_index,
       separators=["\n\n", "\n", ".", " "]
    )

    chunks: list[Document] = splitter.split_documents(documents=documents)
    logger.success(f"Split the combined text of our books into {len(chunks)} chunks")     
    return chunks


def chunk_lengths_beyond_limit(documents: list[Document]):

    embedding_model = SentenceTransformer(config.embedding_model_name)
    max_seq_length = embedding_model.max_seq_length
    logger.warning(f"The embedding model has a maximum sequence length of {max_seq_length}")     

    tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=config.embedding_model_name)
    lengths = [len(tokenizer.encode(document.page_content)) for document in documents]
    lengths_beyond_max = [length for length in lengths if length > max_seq_length]
    
    return True if len(lengths_beyond_max) > 0 else False 


if __name__ == "__main__":
    documents = read_books(books=[neo_colonialism, africa_unite, dark_days])
    chunks = split_documents_into_chunks(documents=documents)
    check = chunk_lengths_beyond_limit(documents=documents)
    breakpoint()
