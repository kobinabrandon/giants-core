from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel


def initiate_llm(model_name: str = "llama-3.3-70b-versatile") -> BaseChatModel:
    return ChatGroq(model=model_name, temperature=0)

