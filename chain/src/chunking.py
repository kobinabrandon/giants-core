from loguru import logger
from transformers import AutoTokenizer
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer    
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.config import config


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


def check_chunk_lengths():

    embedding_model = SentenceTransformer(config.embedding_model_name)
    logger.warning(f"The embedding model has a maximum sequence length of {embedding_model.max_seq_length}")     

    tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=config.embedding_model_name)
    breakpoint()

