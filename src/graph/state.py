from typing import TypedDict
from langchain_core.documents import Document
from langgraph.graph.message import Messages


class ChatState(TypedDict):
    question: str 
    context: list[Document]
    answer: str 
    messages: list[Messages]

