import os
import json
from pathlib import Path

from loguru import logger
from langchain_core.documents import Document

from src.setup.paths import set_paths
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

            Using the information contained in the context, answer the user's question. Respond only to the question asked, but try to make the response as 
            detailed as you can, while staying within the bounds of the context provided. If the answer cannot be deduced from the context, say that you do 
            not know. Where you make reference to specific statements from the context, quote those statements first. Try to avoid repetition.
                
            Context: 
            {context}

            Here is the question: 
            {question}
            """  


def record_responses(
        question: str, 
        context: str, 
        model_name: str, 
        response: str, 
        history: str | None = None, 
        temperature: float | None = None, 
        top_p: float | None = None
) -> None:
    """
    Create directories where the responses for and associated data will be kept, and then store that information 
    for later review. 

    Args:
        response: the response complete response from the LLM 
    """
    DATA_DIR = set_paths()["data"]

    RESPONSES_DIR = DATA_DIR / "responses" 
    MODEL_DIR = RESPONSES_DIR / model_name
    
    for path in [RESPONSES_DIR, MODEL_DIR]:
        if not Path(path).exists():
            os.mkdir(path)

    data_to_save: list[dict[str, str | int | float |None]]  = [
        {
            "top_p": top_p,
            "temperature": temperature,
            "question": question, 
            "context": context,
            "response": response,
            "history": history
        }
    ]   

    attempt = 0 
    name_of_file_to_save: str = f"{shorten_question(question=question)}.json" 
    file_path: Path = MODEL_DIR / name_of_file_to_save
    
    # Save the information associated with this query because it's the first of its kind 
    if not Path(file_path).exists(): 
        data_to_save[0]["attempt"] = attempt
        with open(file_path, mode="w") as file:
            json.dump(data_to_save, file, indent=4)

    else: 
        with open(file_path, mode="rb") as file:
            # Retrieve the data associated with a similar question that was previously asked 
            saved_data: list[dict[str, str | int | float |None]]  = json.load(file)
        
        # Delete the old file
        os.remove(file_path)

        # Mark the current query as a new attempt to answer a similar question
        data_to_save[0]["attempt"]: int = saved_data[-1]["attempt"] + 1
        saved_data.extend(data_to_save)

        with open(file_path, mode="w") as file:
            json.dump(saved_data, file, indent=4)


def shorten_question(question: str) -> str:
    """
    Return the index of the first question mark or full stop that occurs in the question

    Returns:
        str: the truncated question    
    """
    index: list[str] = []

    if ("?" not in question) and ("." not in question):
        return question

    else:
        for character in question:
            if character in ["?", "."]:
                truncated_question = question[: question.index(character) + 1] 
                index.append(truncated_question)
                break

        return index[0] 

