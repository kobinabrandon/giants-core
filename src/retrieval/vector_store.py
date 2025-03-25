from langchain_core.documents import Document
from langchain_core.vectorstores.base import VectorStoreRetriever

from src.data_preparation.sourcing import Author
from src.data_processing.embeddings import ChromaAPI


def get_context(author: Author, question: str, top_k: int = 5) -> str: 
    """
    Query the VectorDB(Chroma for now) to perform a similarity search,  

    Args:
        nickname: 
        question: the question being asked of the model. 
        raw: 

        top_k: 

    Returns:
       str: the text retrieved from the vector database based on a certain similarity metric 
    """
    chroma = ChromaAPI(author=author)
    query_results: list[Document] = chroma.vector_store.similarity_search(query=question, k=top_k)
    raw_results: list[str] = [result.page_content for result in query_results]

    return " ".join(
        [text for text in raw_results]
    )


def get_base_retriever(author: Author, top_k: int = 5) -> VectorStoreRetriever:
    chroma = ChromaAPI(author=author)
    return chroma.vector_store.as_retriever(
        search_kwargs={"k": top_k}
    )

