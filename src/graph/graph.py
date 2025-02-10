from loguru import logger

from langchain import hub
from langchain_chroma.vectorstores import Chroma
from langchain_core.language_models.chat_models import BaseChatModel

from langgraph.graph import StateGraph, START
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from torch.cuda import graph_pool_handle
# from langgraph.checkpoint.memory import MemorySaver
# from langgraph.prebuilt import ToolNode, tools_condition

from src.setup.config import llm_config, State
from src.indexing.embeddings import get_embedding_model
from src.generation.appendix import get_context




def initiate_llm(model_id: str = "meta-llama/Llama-Guard-3-8B", task: str = "text-generation") -> BaseChatModel:

    hf_pipeline = HuggingFacePipeline.from_model_id(model_id=model_id, task=task, low_cpu_mem_usage=True, max_shard_size="500")
    return ChatHuggingFace(llm=hf_pipeline)

def retrieval_node(state: State):
    vector_store = Chroma(embedding_function=get_embedding_model())
    retrieved_docs = vector_store.similarity_search_with_score(query=state["question"])
    return {"context": retrieved_docs}


def generate(state: State):
    prompt = hub.pull("rlm/rag-prompt")
    docs = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke(
        {
            "question": state["question"], 
            "context": get_context(question=state["question"]) 
        } 
    ) 

    llm = initiate_llm()

    response = llm.invoke(messages)
    return {"answer": response.content}


graph_builder = StateGraph(state_schema=State).add_sequence(nodes=[retrieval_node, generate])
graph_builder.add_edge(start_key=START, end_key="retrieval_node")
graph = graph_builder.compile()

response = graph.invoke(
    input={"question": "Why did Nkrumah travel to Asia in February 1966?"}
)

print(response["answer"])


