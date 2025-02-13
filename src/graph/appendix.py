from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel

from src.setup.config import groq_config


def initiate_llm(temperature: int = 0, model_name: str = groq_config.preferred_model) -> BaseChatModel:
    return ChatGroq(model=model_name, temperature=temperature)

