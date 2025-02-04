from loguru import logger

from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline

from src.setup.config import llm_config


def initiate_llm(model_id: str = "LatitudeGames/Wayfarer-12B-GGUF", task: str = "text-generation"):

    hf_pipeline = HuggingFacePipeline.from_model_id(model_id=model_id, task=task, low_cpu_mem_usage=True, max_shard_size="500")
    return ChatHuggingFace(llm=hf_pipeline)


initiate_llm()
