import torch
from loguru import logger
from argparse import ArgumentParser

from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer

from src.setup.config import embed_config 
from src.embeddings import ChromaAPI, PineconeAPI


def get_context(question: str, raw: bool, top_k: int = 3) -> str | list[Document]:
    """
    Query the VectorDB(Chroma for now) to perform a similarity search,  

    Args:
        question: the question being asked of the model. 

    Returns:
       str: the text retrieved from the vector database based on a certain similarity metric 
    """
    chroma = ChromaAPI()
    query_results: list[Document] = chroma.main_store.similarity_search(query=question, k=top_k)

    if not raw:
        return query_results
    else:
        retrieved_results = [result.page_content for result in query_results]

        return "".join(
            [doc for doc in retrieved_results]
        )


def query_pinecone(question: str, multi_index: bool, book_file_name: str | None, top_k: int) -> list[dict[str, str]]:
    
    logger.info("Quering Pinecone...")
    api = PineconeAPI(multi_index=multi_index)
    index = api.get_index(book_file_name=book_file_name)

    device = "gpu" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer(embed_config.embedding_model_name, device=device)

    query_vector = model.encode(question).tolist()
    xc = index.query(vector=query_vector, top_k=top_k, include_metadata=True)
    
    return xc["matches"]

 
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
        results = get_context(question=question, top_k=args.top_k, raw=True)

    breakpoint()

