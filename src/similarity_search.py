import torch
from argparse import ArgumentParser

from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer

from src.config import config
from src.vector_db import ChromaAPI
from src.vector_db import PineconeAPI


def query_pinecone(query: str, multi_index: bool, book_file_name: str | None, top_k: int) -> list[dict]:
   
    api = PineconeAPI(multi_index=multi_index)
    index = api.get_index(book_file_name=book_file_name)

    device = "gpu" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer(config.embedding_model_name, device=device)

    query_vector = model.encode(query).tolist()
    xc = index.query(vector=query_vector, top_k=top_k, include_metadata=True)
    
    return xc["matches"]


def query_chroma(query: str, top_k: int = 5) -> list[tuple[Document, float]]:   

    chroma = ChromaAPI()
    results: list[tuple[Document, float]] = chroma.store.similarity_search_with_score(query=query, k=top_k)
    return results

  
if __name__ == "__main__":
    parser = ArgumentParser()

    _ = parser.add_argument("--pinecone", action="store_true")
    _ = parser.add_argument("--chroma", action="store_true")
    _ = parser.add_argument("--multi_index", action="store_true")
    _ = parser.add_argument("-o", "--book_file_name", nargs="?")
    _ = parser.add_argument("--top_k", type=int)

    args = parser.parse_args()    

    if args.pinecone:
        results = query_pinecone(
                query="What happened on the way to China?", 
                multi_index=args.multi_index, 
                book_file_name=args.book_file_name,
                top_k=args.top_k
        )

    else:
        results = query_chroma(query="How does neocolonialism affect development?", top_k=args.top_k)

    breakpoint()

