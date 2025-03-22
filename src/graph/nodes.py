from langchain_core.documents import Document
# from src.embeddings import get_embedding_model
# from langchain_chroma.vectorstores import Chroma

from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import Messages
from langchain_core.messages.base import BaseMessage
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.language_models.chat_models import BaseChatModel

from src.graph.state import ChatState 
from src.graph.appendix import initiate_llm
from src.vector_store.retrieval import get_context


llm: BaseChatModel = initiate_llm()


@tool(response_format="content_and_artifact")
def make_retrieval_node(state: ChatState, question: str, nickname: str ="fidel") -> tuple[str, list[Document]]:
    """

    Args:
        state: 

    Returns:
        
    """
    retrieved_docs: list[Document] = get_context(nickname=nickname, question=question) 

    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
        for doc in retrieved_docs
    )

    state["question"] = question
    state["context"] = retrieved_docs 
    return serialized, retrieved_docs


tools = ToolNode([make_retrieval_node])


def query_or_response_node(state: ChatState) -> dict[str, list[BaseMessage]]:

    llm_with_tools = llm.bind_tools([make_retrieval_node])
    breakpoint()

    messages_so_far: list[Messages] = state["messages"]
    human_messages = next(m for m in reversed(messages_so_far) if isinstance(m, HumanMessage))
    response = llm_with_tools.invoke(human_messages.content)

    return {
        "messages": [response]
    }


def generate(state: ChatState) -> dict[str, list[BaseMessage]]: 

    recent_tool_messages = [] 

    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)

    tool_messages: list[ToolMessage] = recent_tool_messages[::-1]
    context : str = "\n\n".join(doc.content for doc in tool_messages)

    system_message_content = (
        """You are a helpful chatbot whose job is to answer questions based on the context given to you.
        If the user greets you, respond in kind

        Using the information contained in the context, answer the user's question. Respond only to the question asked, but try to make the response as 
        detailed as you can, while staying within the bounds of the context provided. If the answer cannot be deduced from the context, say that you do 
        not know. Where you make reference to specific statements from the context, quote those statements first. Try to avoid repetition. Here's the 
        context below."""
        "\n\n"
        f"{context}"
    )

    conversation_messages: list[Messages] = [message for message in state["messages"]]

    prompt = [SystemMessage(content=system_message_content)] + conversation_messages
    response: BaseMessage = llm.invoke(prompt)

    return {
        "message": [response]
    }

