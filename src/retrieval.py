import torch
from loguru import logger
from argparse import ArgumentParser

from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer

from src.config import config
from src.embeddings import ChromaAPI, PineconeAPI


def query_pinecone(question: str, multi_index: bool, book_file_name: str | None, top_k: int) -> list[dict]:
    
    logger.info("Quering Pinecone...")
    api = PineconeAPI(multi_index=multi_index)
    index = api.get_index(book_file_name=book_file_name)

    device = "gpu" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer(config.embedding_model_name, device=device)

    query_vector = model.encode(question).tolist()
    xc = index.query(vector=query_vector, top_k=top_k, include_metadata=True)
    
    return xc["matches"]


def query_chroma(question: str, top_k: int = 1) -> list[tuple[Document, float]]:   

    logger.info("Quering ChromaDB...")
    chroma = ChromaAPI()
    results: list[tuple[Document, float]] = chroma.store.similarity_search_with_score(query=question, k=top_k)
    return results

  
if __name__ == "__main__":
    parser = ArgumentParser()

    _ = parser.add_argument("--pinecone", action="store_true")
    _ = parser.add_argument("--chroma", action="store_true")
    _ = parser.add_argument("--multi_index", action="store_true")
    _ = parser.add_argument("-o", "--book_file_name", nargs="?")
    _ = parser.add_argument("--top_k", type=int)

    args = parser.parse_args()    
    question = "Who were the coup plotters?"

    if args.pinecone:
        results = query_pinecone(
                question=question, 
                multi_index=args.multi_index, 
                book_file_name=args.book_file_name,
                top_k=args.top_k
        )

    else:
        results = query_chroma(question=question, top_k=args.top_k)

    breakpoint()

