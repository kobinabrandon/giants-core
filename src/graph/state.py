from typing import TypedDict

from langgraph.graph.message import Messages


class ChatState(TypedDict):
    question: str 
    context: str
    answer: str 
    messages: list[Messages] 

