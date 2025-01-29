from loguru import logger
from langchain_core.documents import Document

from src.retrieval.query import query_chroma


def get_context(question: str) -> str:
    """
    Query the VectorDB(Chroma for now) to perform a similarity search,  

    Args:
        question: the question being asked of the model. 

    Returns:
       str: the text retrieved from the vector database based on a certain similarity metric 
    """
    logger.info("Getting context:")
    query_results: list[tuple[Document, float]] = query_chroma(question=question)
    retrieved_results = [result[0].page_content for result in query_results]

    return "".join(
        [doc for doc in retrieved_results]
    )




def get_prompt(context: str, question: str) -> str:

    return f""" 
            You are a helpful chatbot whose job is to answer questions about Kwame Nkrumah based on the context given to you.
            If the user greets you, respond in kind, emphasising that your purpose is to discuss the life and times of Kwame Nkrumah. 

            Using the information contained in the context, give a comprehensive answer to the question, without mentioning the context with wording like "Based on the context...".
            Respond only to the question asked, but try to make the response as detailed as you can, while staying within the bounds of the context provided. 
            If the answer cannot be deduced from the context, say that you do not know. Where you make reference to specific statements from the context, quote those statements first. 
            Try to avoid repetition.
                
            Context: 
            {context}

            Now here is the question you need to answer: 
            {question}
            """  


