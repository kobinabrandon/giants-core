from langchain_core.documents import Document
from langchain_chroma.vectorstores import Chroma

from langchain_core.tools import tool
from langgraph.graph.message import BaseMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import MessagesState 
from langchain_core.messages import SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel

from src.setup.config import State
from src.graph.appendix import initiate_llm
from src.indexing.embeddings import get_embedding_model
from src.generation.appendix import get_context, get_prompt


def establish_state(question: str) -> tuple[str, str]:
    return question, get_context(question=question)


# @tool(response_format="content_and_artifact")
def make_retrieval_node(state: State) -> dict[str, list[Document]]:
    """

    Args:
        state: 

    Returns:
        
    """
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

    llm: BaseChatModel = initiate_llm()

    response = llm.invoke(prompt)
    return {"answer": response.content}


def query_or_response_node(state: MessagesState):
    llm = initiate_llm() 
    llm_with_tools = llm.bind_tools([make_retrieval_node])

    response = llm_with_tools.invoke(
        state["messages"]
    )

    return {"messages": [response]}


tools = ToolNode([make_retrieval_node])


def generate(state: MessagesState, llm: BaseChatModel) -> dict[str, list[BaseMessage]]: 

    recent_tool_messages = [] 

    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)

    tool_messages = recent_tool_messages[::-1]
    docs_content: str = "\n\n".join(doc.content for doc in tool_messages)

    system_message_content = (
        "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you don't know." 
        "\n\n"
        f"{docs_content}"
    )

    conversation_messages = [
        message 
        for message in state["messages"] 
        if message.type in ["human", "system"]
        or (message.type == "ai") and (not message.tool_calls)
    ]

    prompt = [SystemMessage(content=system_message_content)] + conversation_messages
    response: BaseMessage = llm.invoke(prompt)

    return {
        "message": [response]
    }

