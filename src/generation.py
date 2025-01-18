import requests

from argparse import ArgumentParser

from openai import OpenAI
from huggingface_hub import InferenceClient
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma, Pinecone
from langchain_core.vectorstores import VectorStoreRetriever

from src.config import config 
from src.retrieval import query_chroma


class ViaHTTP:
    def __init__(self, question: str) -> None:
        self.question: str = question
        self.context: str = get_context(question=question)

    def send_request(self):

        headers = {
            "Accept" : "application/json",
            "Authorization": f"Bearer {config.hugging_face_token}",
            "Content-Type": "application/json" 
        }

        payload: dict[str, dict[str, str]] = {
            "inputs": {
               "context": self.context, 
               "question": self.question
            }
        }

        response = requests.post(config.llm_endpoint_url, headers=headers, json=payload)
        return response.json()
    

class ViaClient:
    def __init__(self, question: str) -> None:
        self.question: str = question
        self.client = InferenceClient(model=config.llm_endpoint_url, token=config.hugging_face_token)

    def send_request(
        self, 
        method: str, 
        use_open_ai: bool, 
        temperature: float | None = None
    ):
        context = get_context(question=self.question)

        if method.lower() == "qa":
            response = self.client.question_answering(question=self.question, context=context)

        elif method.lower() == "generation" and not use_open_ai:
            prompt = make_prompt_template(question=self.question, context=context)
            response = self.client.text_generation(prompt=prompt, temperature=temperature)

        elif method.lower() == "generation" and use_open_ai:
            client = OpenAI(base_url=config.llm_endpoint_url, api_key=config.hugging_face_token)

            chat_completion = client.chat.completions.create(
                model="tgi",
                top_p=None,
                temperature=None,
                max_tokens=500,
                stream=True,
                messages=[
                    {
                        "role": "user",
                        "content": self.question 
                    }
                ]
            )

            for message in chat_completion:
                print(message.choices[0].delta.content, end="")


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
            Using the information contained in the context, give a comprehensive answer to the question. 
            Respond only to the question asked, response should be as detailed as you can make it, based on the context provided. 
            If the answer cannot be deduced from the context, do not give an answer.
                
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
    _ = parser.add_argument("--request_type", type=str)
    _ = parser.add_argument("--method", type=str)
    _ = parser.add_argument("--use_open_ai", action="store_true")

    args = parser.parse_args()
    question = "Who were the coup plotters?"

    if args.request_type == "http_request":
        requester = ViaHTTP(question=question)    
        response = requester.send_request()
        breakpoint()

    elif args.request_type == "client":
        requester = ViaClient(question=question)
        response = requester.send_request(method=args.method, use_open_ai=args.use_open_ai)
        breakpoint()

