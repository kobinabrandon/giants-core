from numpy import who
import torch 
from transformers import PreTrainedTokenizer
from transformers.pipelines.base import Pipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, pipeline

from src.config import config 


# bnb_config = BitsAndBytesConfig(
#     load_in_4bit=True,
#     bnb_4bit_use_double_quant=True,
#     bnb_4bit_quant_type="nf4",
#     bnb_4bit_compute_dtype=torch.bfloat16,
# )
#


def make_reader_llm(reading_model_name: str = config.reading_model_name, tokenizer: PreTrainedTokenizer) -> Pipeline:

    llm = AutoModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path=reading_model_name,
        torch_dtype=torch.bfloat16,
        low_cpu_mem_usage=True
    )

    return pipeline(model=llm, tokenizer=tokenizer, task="text-generation")


def make_prompt(question: str, context: str, tokenizer: PreTrainedTokenizer):
    
    prompt_format = [
        {
            "role": "system",
            "content": """ Using the information contained in the context, give a comprehensive answer to the question.
                           Respond only to the question asked, response should be concise and relevant to the question.
                           Provide the number of the source document when relevant. If the answer cannot be deduced 
                           from the context, do not give an answer.""",
        },
        {
           "role": "user",
            "content": f"""Context: {context}
            ---
            Now here is the question you need to answer.
            Question: {question}""",
        }
    ]

    RAG_PROMPT_TEMPLATE = tokenizer.apply_chat_template(
        prompt_format, tokenize=False, add_generation_prompt=True
    )

    print(RAG_PROMPT_TEMPLATE)


def get_tokenizer(reading_model_name: str = config.reading_model_name) -> PreTrainedTokenizer:
    return AutoTokenizer.from_pretrained(pretrained_model_name_or_path=reading_model_name)








