import json
import torch
import pandas as pd

from tqdm import tqdm
from pathlib import Path
from loguru import logger 
from sentence_transformers import SentenceTransformer

from src.setup.config import config 
from src.setup.paths import CHUNK_DETAILS_DIR
from src.feature_pipeline.preprocessing import process_book
from src.feature_pipeline.data_extraction import Book, neo_colonialism, africa_unite, dark_days


def make_embedding_model(books: list[Book]) -> None:

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    embedding_model = SentenceTransformer(model_name_or_path=config.sentence_transformer_name, device=device)
    logger.info("Creating embeddings from chunks of text in each book") 
    
    for book in books: 
        data_file = CHUNK_DETAILS_DIR/f"{book.file_name}.json" 

        if Path(data_file).exists():
            logger.success(f"The sentences of '{book.title}' have already been grouped into chunks")
            with open(data_file, mode="r") as file:
                chunk_details = json.load(file)
        else:
            chunk_details: list[dict[str, str|int]] = process_book(book=book, use_spacy=True, describe=False)                        
        
        for chunk in tqdm(
                iterable=chunk_details, 
                desc=f"Parsing the chunks of sentences from '{book.title}' to make embeddings for each of them"
            ):

            chunks_of_text: str = chunk["merged_chunk"]
            chunk["embeddings"] = embedding_model.encode(chunks_of_text, batch_size=config.batch_size_for_embedding, convert_to_tensor=True)
            
        chunk_details_with_embeddings = pd.DataFrame(data=chunk_details)
        chunk_details_with_embeddings.to_csv(CHUNK_DETAILS_DIR/f"{book.file_name}.csv")


if __name__ == "__main__":
    books = [neo_colonialism, africa_unite, dark_days]
    embeddings = make_embedding_model(books=books)

