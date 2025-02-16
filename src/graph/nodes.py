from langchain_core.documents import Document
# from src.embeddings import get_embedding_model
# from langchain_chroma.vectorstores import Chroma

from langchain_core.tools import tool
from langgraph.graph.message import BaseMessage, Messages
from langgraph.prebuilt import ToolNode
from langgraph.graph import MessagesState 
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel

from src.retrieval import get_context
from src.graph.state import ChatState 
from src.graph.appendix import initiate_llm
from src.generation.appendix import get_prompt


llm: BaseChatModel = initiate_llm()


@tool(response_format="content_and_artifact")
def make_retrieval_node(state: ChatState) -> tuple[str,str]:
    """

    Args:
        state: 

    Returns:
        
    """
    retrieved_docs: list[Document] = get_context(question=state["question"], raw=False) 

    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
        for doc in retrieved_docs
    )

    # state["context"] =  
    return serialized, retrieved_docs 


def retrieval_node(state: ChatState) -> dict[str, str]:
    raw_context : str = get_context(question=state["question"], raw=True) 
    state["context"] = raw_context 
    return {"context": raw_context} 


tools = ToolNode([make_retrieval_node])


def make_generator_node(state: ChatState) -> dict[str, str]:

    prompt = get_prompt(
        context=state["context"],
        question=state["question"]
    )


    response: BaseMessage = llm.invoke(prompt)
    state["answer"] = str(response.content) 
    return {"answer": state["answer"]}


def generate(state: ChatState) -> dict[str, list[BaseMessage]]: 

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
    state["answer"] = response
    return {
        "message": [response]
    }


# def query_or_response_node(state: ChatState):
#     llm = initiate_llm() 
#     llm_with_tools = llm.bind_tools([make_retrieval_node])
#
#     response = llm_with_tools.invoke(
#         state["messages"]
#     )
#
#     return {"messages": [response]}
#

