import os 

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

_  = load_dotenv()


class SectionConfig(BaseSettings):
    _ = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    chunk_size: int = 800
    chunk_overlap: int = 30
    add_start_index: bool = True 
    length_function: object = len
    embedding_model_name: str = "thenlper/gte-large"
    pinecone_api_key: str = os.environ["PINECONE_API_KEY"]
    pinecone_embedding_model: str = "multilingual-e5-large"
    llm_api_url: str = "https://api-inference.huggingface.co/models/timpal0l/mdeberta-v3-base-squad2"
    hugging_face_tokens: str = os.environ["HUGGING_FACE_TOKEN"]

config = SectionConfig()

