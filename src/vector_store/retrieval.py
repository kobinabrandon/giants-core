from argparse import ArgumentParser

from langchain_core.documents import Document

from src.data_preparation.sourcing import Author
from src.vector_store.embeddings import ChromaAPI
from src.data_preparation.authors import prepare_sources


def get_context(nickname: str, question: str, top_k: int = 5) -> list[Document]:
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

    return query_results
    

def get_author(nickname: str) -> Author | None:

    matching_authors: list[Author] = [author for author in prepare_sources() if nickname in author.name.lower()]

    if len(matching_authors) == 0:
        raise Exception(f"The nickname {nickname} doesn't correspond to any existing author")
    elif len(matching_authors) == 1:
        # logger.warning(f"Querying {matching_authors[0].name}'s vector database")
        return matching_authors[0]
    else:
        raise Exception(f"The nickname {nickname} correponds to {len(matching_authors)} authors. Pick a better nickname!")


def get_prompt(context: str, question: str) -> str:

    return f""" 
            You are a helpful chatbot whose job is to answer questions based on the context given to you. If the user greets you, respond in kind.
            Using the information contained in the context, answer the user's question. Respond only to the question asked, but try to make the response as 
            detailed as you can, while staying within the bounds of the context provided. If the answer cannot be deduced from the context, say that you do 
            not know. Where you make reference to specific statements from the context, quote those statements first. Try to avoid repetition.
                
            Context: 
            {context}

            Here is the question: 
            {question}
            """  


# def record_responses(
#         question: str, 
#         context: str, 
#         model_name: str, 
#         response: str, 
#         history: str | None = None, 
#         temperature: float | None = None, 
#         top_p: float | None = None
# ) -> None:
#     """
#     Create directories where the responses for and associated data will be kept, and then store that information 
#     for later review. 
#
#     Args:
#         response: the response complete response from the LLM 
#     """
#     DATA_DIR = set_paths()["data"]
#
#     RESPONSES_DIR = DATA_DIR / "responses" 
#     MODEL_DIR = RESPONSES_DIR / model_name
#
#     for path in [RESPONSES_DIR, MODEL_DIR]:
#         if not Path(path).exists():
#             os.mkdir(path)
#
#     data_to_save: list[dict[str, str | int | float |None]]  = [
#         {
#             "top_p": top_p,
#             "temperature": temperature,
#             "question": question, 
#             "context": context,
#             "response": response,
#             "history": history
#         }
#     ]   
#
#     attempt = 0 
#     name_of_file_to_save: str = f"{shorten_question(question=question)}.json" 
#     file_path: Path = MODEL_DIR / name_of_file_to_save
#
#     # Save the information associated with this query because it's the first of its kind 
#     if not Path(file_path).exists(): 
#         data_to_save[0]["attempt"] = attempt
#         with open(file_path, mode="w") as file:
#             json.dump(data_to_save, file, indent=4)
#
#     else: 
#         with open(file_path, mode="rb") as file:
#             # Retrieve the data associated with a similar question that was previously asked 
#             saved_data: list[dict[str, str | int | float |None]]  = json.load(file)
#
#         # Delete the old file
#         os.remove(file_path)
#
#         # Mark the current query as a new attempt to answer a similar question
#         data_to_save[0]["attempt"]: int = saved_data[-1]["attempt"] + 1
#         saved_data.extend(data_to_save)
#
#         with open(file_path, mode="w") as file:
#             json.dump(saved_data, file, indent=4)
#

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


    
     
if __name__ == "__main__":
    parser = ArgumentParser()
    _ = parser.add_argument("--nickname", type=str)
    _ = parser.add_argument("--question", type=str)

    args = parser.parse_args()    
    results = get_context(nickname=args.nickname, question=args.question)
    print(results)

