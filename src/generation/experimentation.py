import requests
from argparse import ArgumentParser

from huggingface_hub import InferenceClient
from langchain_community.vectorstores import Chroma, Pinecone
from langchain_core.vectorstores import VectorStoreRetriever

from src.setup.config import config 
from src.generation.appendix import get_context, get_prompt


class ExperimentalGeneration:
    def __init__(self, task: str, question: str) -> None:
        self.task: str = task 
        self.question: str = question
        self.context: str = get_context(question=question)
        self.prompt: str = get_prompt(question=self.question, context=self.context)

    def send_request(self, max_tokens: int, use_client: bool, use_open_ai: bool, temperature: float | None = None):
        
        if self.task == "text_generation" and not use_client and not use_open_ai:

            headers = {
                "Accept" : "application/json",
                "Authorization": f"Bearer {config.hugging_face_token}",
                "Content-Type": "application/json" 
            }

            payload: dict[str, dict[str, str]] = {
               "inputs": self.prompt, 
                "parameters":{
                    "max_new_tokens": max_tokens
                }
            }

            response = requests.post(url=config.preferred_llm_endpoint_url, headers=headers, json=payload)
            return response.json()
 
        elif self.task == "text_generation" and use_client and not use_open_ai:

            client = InferenceClient(model=config.llm_endpoint_url, token=config.hugging_face_token)
            response = client.text_generation(prompt=self.prompt, temperature=temperature)
            return response.json()

        elif self.task == "text_generation" and use_client and use_open_ai:
            client = OpenAI(base_url=config.preferred_llm_endpoint_url, api_key=config.hugging_face_token)

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
            return response


def get_retriever(top_k: int, vector_db: str = "Chroma") -> VectorStoreRetriever:

    if vector_db.lower() == "chroma":
        return Chroma.as_retriever(search_type="similarity", search_kwargs={"k": top_k})
    elif vector_db.lower() == "pinecone":
        return Pinecone.as_retriever(search_type="similarity", search_kwargs={"k": top_k})
    else:
        return NotImplemented("The requested vector base has not been used.")


if __name__ == "__main__":
    parser = ArgumentParser()
    _ = parser.add_argument("--task", type=str)
    args = parser.parse_args()

    question = "Who were the plotters of the coup against Nkrumah?"

    if args.task== "text_generation":
        requester = ExperimentalGeneration(task=args.task, question=question) 
        response_json = requester.send_request(max_tokens=2000, use_client=True, use_open_ai=True)
        print(response_json)

