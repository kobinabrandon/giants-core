import torch

from index import PineconeAPI
from sentence_transformers import SentenceTransformer

from general.books import Book
from config import config

from chunking import split_text_into_chunks


def query_embeddings(query: str):
   
    api = PineconeAPI()
    index = api.get_index(name=config.pinecone_index)

    device = "gpu" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer(config.sentence_transformer_name, device=device)

    query_vector = model.encode(query).tolist()
    xc = index.query(vector=query_vector, top_k=5, include_metadata=True)

    breakpoint()

if __name__ == "__main__":
    query_embeddings(query="What is neocolonialism?")

