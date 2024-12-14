import json
import torch
import numpy as np
import pandas as pd

from tqdm import tqdm
from pathlib import Path
from loguru import logger 

from sentence_transformers import SentenceTransformer

from src.config import config 
from src.processing import process_book

from general.config import general_config 
from general.paths import make_data_directories
from general.books import Book, neo_colonialism, africa_unite, dark_days


device = general_config.device

def get_embedding_model(model_name: str) -> SentenceTransformer:
    return SentenceTransformer(model_name_or_path=model_name, device=device)

def make_embeddings_of_chunks(book: Book, model_name: str = config.sentence_transformer_name) -> None:
    
    logger.info(f"Creating embeddings from chunks of text in '{book.title}'") 
    embedding_model = get_embedding_model(model_name=model_name)
    
    CHUNK_DETAILS_DIR = config.paths["chunk_details"]
    data_file = CHUNK_DETAILS_DIR/f"{book.file_name}.json" 

    if Path(data_file).exists():
        logger.success(f"The sentences of '{book.title}' have already been grouped into chunks")
        with open(data_file, mode="r") as file:
            chunk_details = json.load(file)
    else:
        chunk_details: list[dict[str, str|int]] = process_book(book=book, use_spacy=True, describe=False)                        
    
    for chunk in tqdm(iterable=chunk_details, desc=f"Parsing chunks of text from '{book.title}' to make embeddings for each of them"):
        chunk_of_text: str = chunk["merged_chunk"]
        chunk["embedding"] = embedding_model.encode(chunk_of_text, batch_size=config.batch_size_for_embedding, convert_to_tensor=True)
        
    embeddings_path = set_embeddings_path(book=book)
    chunk_details_with_embeddings = pd.DataFrame(data=chunk_details)
    chunk_details_with_embeddings.to_csv(embeddings_path)


def set_embeddings_path(book: Book) -> Path:
    EMBEDDINGS_DIR = config.paths["embeddings"]
    return EMBEDDINGS_DIR / f"{book.file_name}.csv"  


def retrieve_embeddings_of_chunks(book: Book, model_name: str = config.sentence_transformer_name):

    embedding_path = set_embeddings_path(book=book) 
    
    if not Path(embedding_path).exists():
        make_embeddings_of_chunks(book=book, model_name=model_name)
    
    chunk_details_and_embeddings: pd.DataFrame = pd.read_csv(embedding_path)
    chunk_details_and_embeddings["embedding"] = chunk_details_and_embeddings["embedding"].apply(lambda x: np.fromstring(x.strip("[]")))

    array_to_embed = np.array(chunk_details_and_embeddings["embedding"].tolist())
        
    embedding = torch.tensor(array_to_embed).to(device=device)
    return embedding


if __name__ == "__main__":
    make_data_directories(from_scratch=True, general=False)
    for book in [neo_colonialism, africa_unite, dark_days]:
        book.download()
        make_embeddings_of_chunks(book=book)





#retrieve_embeddings(book=neo_colonialism)
