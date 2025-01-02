from huggingface_hub import InferenceClient

from src.config import config
from src.similarity_search import query_chroma


def make_client(model_id: str = config.llm_endpoint_url) -> InferenceClient:
    return InferenceClient(model=model_id, token=config.hugging_face_token)


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


def test(question: str = "Using the context that you have, tell me as much about neo-colonialism as you can?"):

    question_results: list[tuple[Document, float]] = query_chroma(query=question)
    retrieved_results = [result[0].page_content for result in question_results]

    context = "\n Extracted documents: \n"
    context += "".join(
        [f"\n" + doc for doc in retrieved_results]
    )

    client = make_client()
    # prompt = make_prompt_template(question=question, context=context)
    response = client.question_answering(question=question, context=context)
    breakpoint()


if __name__ == "__main__":
    client = test()
    


 


 


 


 


 


 


 


 


 


 


 


 


 


 


 


 


 


 


 


 


 


 



