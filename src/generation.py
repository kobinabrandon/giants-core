import os
import json
from pathlib import Path
from loguru import logger
from openai import OpenAI
from langchain_core.documents import Document

from src.config import config 
from src.paths import set_paths
from src.retrieval import query_chroma


def query_primary_llm(
        question: str, 
        top_p: float | None,
        max_tokens: int = 2000, 
        temperature: int | None = 0, 
        save_data: bool = True,
        model_name: str = "wayfarer-12b-gguf-hva"
) -> None:
    """
    Gets the context, and uses it (as well as the question) to construct a prompt.
    
    Args:
        question: the question being asked of the LLM
        max_tokens: the maximum number of tokens in the generated answer 
        temperature: the level of randomness in the choice of the next letter 
        top_p: a floating point number that controls the variety of words to be considered 
        save_data: whether the question and the resulting answer will be logged. 
    """
    assert model_name in config.endpoints_under_consideration.keys()

    logger.info("Getting context:")
    context: str = get_context(question=question)

    logger.info("Creating prompt..")
    prompt: str = construct_prompt(question=question, context=context)
    
    endpoint_url: str = config.endpoints_under_consideration[model_name] 
    client = OpenAI(base_url=endpoint_url, api_key=config.hugging_face_token)

    logger.info("Prompting model...")
    chat_completion = client.chat.completions.create(
        model="tgi",
        top_p=top_p,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
        messages=[
            {
                "role": "user",
                "content": prompt 
            }
        ]
    )
    
    logger.success("Answering query. Stand by:")

    response_characters: list[str] = [""]
    for message in chat_completion:
        letters_in_the_response: str | None = message.choices[0].delta.content
        print(letters_in_the_response, end="")

        if isinstance(letters_in_the_response, str) :
            response_characters.append(letters_in_the_response)
           
    if save_data:
         
        full_response = "" 
        for i in response_characters:
            full_response += i

        record_responses(question=question, context=context, response=full_response, model_name=model_name) 
        logger.success("Saved the question and the answer")


def get_context(question: str) -> str:
    """
    Query the VectorDB(Chroma for now) to perform a similarity search,  

    Args:
        question: the question being asked of the model. 

    Returns:
       str: the text retrieved from the vector database based on a certain similarity metric 
    """
    query_results: list[tuple[Document, float]] = query_chroma(question=question)
    retrieved_results = [result[0].page_content for result in query_results]

    return "".join(
        [doc for doc in retrieved_results]
    )


def construct_prompt(question: str, context: str) -> str:

    return f""" 
            You are a helpful chatbot whose job is to answer questions based on the context given to you. Using the information contained in the context, give a comprehensive answer to the question. 
            Respond only to the question asked, but try to make the response as detailed as you can, while staying within the bounds of the context provided. 
            If the answer cannot be deduced from the context, say that you do not know. Where you make reference to specific statements from the context, quote those statements first. Try to avoid repetition.
                
            Context: 
            {context}

            Now here is the question you need to answer: 
            {question}
            """  


def record_responses(question: str, context: str, response: str, model_name: str) -> None:
    """
    Create directories where the responses for and associated data will be kept, and then store that information 
    for later review. 

    Args:
        response: the response complete response from the LLM 
    """
    DATA_DIR = set_paths()["data"]

    RESPONSES_DIR = DATA_DIR / "responses" 
    MODEL_DIR = RESPONSES_DIR / model_name
    QUESTIONS_DIR = MODEL_DIR / shorten_question(question=question) 
    
    for path in [RESPONSES_DIR, MODEL_DIR, QUESTIONS_DIR]:
        if not Path(path).exists():
            os.mkdir(path)

    data_to_save: dict[str, str] = {
        "question": question, 
        "context": context,
        "response": response
    }

    with open(QUESTIONS_DIR / f"{model_name}.json" , mode="w") as file:
        json.dump(data_to_save, file)


def shorten_question(question: str) -> str:
    """
    Return the index of the first question mark or full stop that occurs in the question

    Args:
        question: 

    Returns:
        
    """
    index: list[str] = []
    for character in question:
        if character in ["?", "."]:
            index.append(
                question[: question.index(character) + 1] 
            )
        
            break
    
    return index[0] 

if __name__ == "__main__":
    query_primary_llm(
        question="How did Nkrumah find out that he had been overthrown?",
        top_p=None,
        temperature=None,
    )
