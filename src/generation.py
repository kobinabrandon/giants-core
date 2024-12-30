import requests
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma, Pinecone
from langchain_core.vectorstores import VectorStoreRetriever

from src.config import config


def make_prompt(context: str, query: str) -> PromptTemplate:

    template = f"""
    Based on the following context: {context}, answer the following question: 
    {query}
    """
    return PromptTemplate(input_variables=[context, query], template=template)


def get_retriever(top_k: int, vector_db: str = "Chroma") -> VectorStoreRetriever:
    
    if vector_db.lower() == "chroma":
        return Chroma.as_retriever(search_type="similarity", search_kwargs={"k": top_k})
    elif vector_db.lower() == "pinecone":
        return Pinecone.as_retriever(search_type="similarity", search_kwargs={"k": top_k})
    else:
        return NotImplemented("The requested vector base has not been used.")


def get_response(context: str):

    payload = {
                "inputs": {
                    "context": context, 
                    "question": "Tell me more about neocolonialism"
                }
              }

    headers = {"Authorization": f"Bearer {config.hugging_face_tokens}"}

    response = requests.post(url=config.llm_api_url, headers=headers, json=payload) 
    return response.json()


output = get_response()
print(output)
