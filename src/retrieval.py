from argparse import ArgumentParser

from loguru import logger
from langchain_core.documents import Document

from src.embeddings import ChromaAPI
from src.authors import prepare_sources
from src.data_preparation.sourcing import Author


def get_context(nickname: str, question: str, raw: bool, top_k: int = 5) -> str | list[Document]:
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
    author: Author | None = get_author(nickname=nickname)

    assert author != None
    chroma = ChromaAPI(author=author)
    query_results: list[Document] = chroma.vector_store.similarity_search(query=question, k=top_k)

    if not raw:
        return query_results
    else:
        retrieved_results = [result.page_content for result in query_results]

        return "".join(
            [doc for doc in retrieved_results]
        )


def get_author(nickname: str) -> Author | None:

    matching_authors: list[Author] = [author for author in prepare_sources() if nickname in author.name.lower()]

    if len(matching_authors) == 0:
        raise Exception(f"The nickname {nickname} doesn't correspond to any existing author")
    elif len(matching_authors) == 1:
        logger.warning(f"Querying {matching_authors[0].name}'s vector database")
        return matching_authors[0]
    else:
        raise Exception(f"The nickname {nickname} correponds to {len(matching_authors)} authors. Pick a better nickname!")

    
     
if __name__ == "__main__":
    parser = ArgumentParser()
    _ = parser.add_argument("--nickname", type=str)
    _ = parser.add_argument("--question", type=str)

    args = parser.parse_args()    
    results = get_context(nickname=args.nickname, question=args.question, raw=True)
    print(results)

