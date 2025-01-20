import requests

from argparse import ArgumentParser

from openai import OpenAI
from huggingface_hub import InferenceClient
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma, Pinecone
from langchain_core.vectorstores import VectorStoreRetriever

from src.config import config 
from src.retrieval import query_chroma


class API:
    def __init__(self, task: str, question: str) -> None:
        self.task: str = task 
        self.question: str = question
        self.context: str = get_context(question=question)
        self.prompt = make_prompt_template(question=self.question, context=self.context)
        breakpoint()

    def send_request(self, max_tokens: int, use_client: bool, use_open_ai: bool, temperature: float | None = None):
        
        if self.task == "text_generation" and not use_client and not use_open_ai:

            headers = {
                "Accept" : "application/json",
                "Authorization": f"Bearer {config.hugging_face_token}",
                "Content-Type": "application/json" 
            }

            payload: dict[str, dict[str, str]] = {
               "inputs": self.question, 
                "parameters":{
                    "max_new_tokens": max_tokens
                }
            }

            response = requests.post(url=config.llm_endpoint_url, headers=headers, json=payload)
            return response.json()
 
        elif self.task == "text_generation" and use_client and not use_open_ai:

            client = InferenceClient(model=config.llm_endpoint_url, token=config.hugging_face_token)
            response = client.text_generation(prompt=self.prompt, temperature=temperature)
            return response.json()

        elif self.task == "text_generation" and use_client and use_open_ai:
            client = OpenAI(base_url=config.llm_endpoint_url, api_key=config.hugging_face_token)

            chat_completion = client.chat.completions.create(
                model="tgi",
                top_p=None,
                temperature=None,
                max_tokens=max_tokens,
                stream=True,
                messages=[
                    {
                        "role": "user",
                        "content": self.prompt
                    }
                ]
            )

            for message in chat_completion:
                print(message.choices[0].delta.content, end="")
       
        elif self.task == "qa":
            client = InferenceClient(model=config.llm_endpoint_url, token=config.hugging_face_token)
            response = client.question_answering(question=self.question, context=self.context)
            return response.json()

def get_context(question: str) -> str:
    """
    Query the VectorDB(Chroma for now) to perform a similarity search,  

    Args:
        question: 

    Returns:
        
    """
    query_results: list[tuple[Document, float]] = query_chroma(question=question)
    retrieved_results = [result[0].page_content for result in query_results]

    context = "".join(
        [doc for doc in retrieved_results]
    )

    return context 


def make_prompt_template(question: str, context: str) -> str:

    return f""" 
            You are a helpful chatbot whose job is to answer questions based on the context given to you. Using the information contained in the context, give a comprehensive answer to the question. 
            Respond only to the question asked, but try to make the response as detailed as you can, while staying within the bounds of the context provided. 
            If the answer cannot be deduced from the context, say that you do not know. Where you make reference to specific statements from the context, quote those statements first. Try to avoid repetition.
                
            Context: 
            {context}

            Now here is the question you need to answer: 
            {question}
            """


# def get_retriever(top_k: int, vector_db: str = "Chroma") -> VectorStoreRetriever:
#
#     if vector_db.lower() == "chroma":
#         return Chroma.as_retriever(search_type="similarity", search_kwargs={"k": top_k})
#     elif vector_db.lower() == "pinecone":
#         return Pinecone.as_retriever(search_type="similarity", search_kwargs={"k": top_k})
#     else:
#         return NotImplemented("The requested vector base has not been used.")


if __name__ == "__main__":
    parser = ArgumentParser()
    _ = parser.add_argument("--task", type=str)

    args = parser.parse_args()
    question = "How did Kwame Nkrumah feel when he was overthrown?"

    if args.task== "text_generation":
        requester = API(task=args.task, question=question) 
        response_json = requester.send_request(max_tokens=2000, use_client=True, use_open_ai=True)
        print(response_json)
        breakpoint()

