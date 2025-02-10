from langchain import hub
from langchain_core.documents import Document
from langchain_chroma.vectorstores import Chroma
from langchain_core.language_models.chat_models import BaseChatModel

from langgraph.graph import StateGraph, START
from langchain_groq import ChatGroq

from src.setup.config import State
from src.indexing.embeddings import get_embedding_model
from src.generation.appendix import get_context, get_prompt


def initiate_llm(model_name: str = "llama-3.3-70b-versatile") -> BaseChatModel:
    return ChatGroq(model=model_name, temperature=0)


def establish_state(question: str) -> tuple[str, str]:
    return question, get_context(question=question)


def make_retrieval_node(state: State) -> dict[str, list[Document]]:
    embedding_model = get_embedding_model()
    vector_store = Chroma(embedding_function=embedding_model)
    retrieved_docs: list[Document] = vector_store.similarity_search(query=state["question"])
    return {"context": retrieved_docs}


def make_generator_node(state: State) -> dict[str, str]:
    state["context"] = get_context(question=state["question"])
    
    prompt = get_prompt(
        context=state["context"],
        question=state["question"]
    )

    llm = initiate_llm()

    response = llm.invoke(prompt)
    return {"answer": response.content}


def build_graph():

    graph_builder = StateGraph(state_schema=State).add_sequence(
        nodes=[make_retrieval_node, make_generator_node]
    )

    graph_builder.add_edge(start_key=START, end_key="make_retrieval_node")
    graph = graph_builder.compile()

    response = graph.invoke(
        input={"question": "What were Nkrumah's views around armed struggle?"}
    )
    
    return response["answer"]


print(
    build_graph()
)

