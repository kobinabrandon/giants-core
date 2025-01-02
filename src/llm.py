import requests
from openai import OpenAI
from langchain_core.documents import Document


from src.config import config 
from src.similarity_search import query_chroma


class Generator:
    def __init__(self)

# headers = {
# 	"Accept" : "application/json",
# 	"Authorization": f"Bearer {config.hugging_face_token}",
# 	"Content-Type": "application/json" 
# }

# client = OpenAI(base_url=config.reading_model_name, api_key=config.hugging_face_token)
#
# chat_completion = client.chat.completions.create(
#     model="tgi",
#     top_p=None,
#     temperature=None,
#     max_tokens=500,
#     stream=True,
#     messages=[
#         {
#             "role": "user",
#             "content": "What is neo-colonialism?"
#         }
#     ]
# )
#
# for message in chat_completion:
#     print(message.choices[0].delta.content, end="")
#

def get_context(query: str = "What is neo-colonialism?"):

    query_results: list[tuple[Document, float]] = query_chroma(query=query)
    retrieved_results = [result[0].page_content for result in query_results]

    context = "\n Extracted documents: \n"
    context += "".join(
        [doc for doc in retrieved_results]
    )

    return context 

headers = {
	"Accept" : "application/json",
	"Authorization": f"Bearer {config.hugging_face_token}",
	"Content-Type": "application/json" 
}

def query(payload):
	response = requests.post(config.llm_endpoint_url, headers=headers, json=payload)
	return response.json()


output = query(
    {
        "inputs": {
           "context": get_context(), 
           "question": "What is neo-colonialism?",
           "parameters": {}
        }

    }
)

print(output)

breakpoint()
