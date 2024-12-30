import torch 
from transformers import PreTrainedTokenizer
from langchain_core.documents import Document
from transformers.pipelines.base import Pipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, pipeline

from src.config import config 
from src.similarity_search import query_chroma

# bnb_config = BitsAndBytesConfig(
#     load_in_4bit=True,
#     bnb_4bit_use_double_quant=True,
#     bnb_4bit_quant_type="nf4",
#     bnb_4bit_compute_dtype=torch.bfloat16,
# )
#


def make_reader_llm(reading_model_name: str = config.reading_model_name ) -> Pipeline:

    tokenizer = get_tokenizer()

    llm = AutoModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path=reading_model_name,
        torch_dtype=torch.bfloat16,
        low_cpu_mem_usage=True
    )

    return pipeline(model=llm, tokenizer=tokenizer, task="text-generation")


def make_prompt_template(question: str, context: str, tokenizer: PreTrainedTokenizer):
    
    prompt_format = [
        {
            "role": "system",
            "content": """ Using the information contained in the context, 
give a comprehensive answer to the question. 
Respond only to the question asked, response should be concise and relevant to the question.
Provide the number of the source document when relevant. If the answer cannot be deduced from the context, do not give an answer.""",
        },
        {
           "role": "user",
            "content": f"""Context: {context}
            ---
            Now here is the question you need to answer.
            Question: {question}""",
        }
    ]

    return tokenizer.apply_chat_template(prompt_format, tokenize=False, add_generation_prompt=True)


def test_reader(query: str = "What is neo-colonialism?"):

    query_results: list[tuple[Document, float]] = query_chroma(query=query)
    retrieved_results = [result[0].page_content for result in query_results]

    context = "\n Extracted documents: \n"
    context += "".join(
        [f"Document {str(i)}:::\n" + doc for i, doc in enumerate(retrieved_results)]
    )

    final_prompt = make_prompt_template(question=query, context=context, tokenizer=get_tokenizer()) 
    reader_llm = make_reader_llm()
    answer = reader_llm(final_prompt)[0]["generated_text"]
    breakpoint()


def get_tokenizer() -> PreTrainedTokenizer:
    return AutoTokenizer.from_pretrained(pretrained_model_name_or_path=config.reading_model_name)


test_reader()

