from typing import TypedDict
from langgraph.graph.message import Messages


class ChatState(TypedDict):
    question: str 
    context: str | list[str]
    answer: str 
    messages: list[Messages]

