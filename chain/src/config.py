import os 

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

_  = load_dotenv()


class SectionConfig(BaseSettings):
    _ = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    chunk_size: int = 200
    chunk_overlap: int = 30
    length_function: object = len
    add_start_index: bool = True 
    sentence_transformer_name: str = "all-mpnet-base-v2"
    pinecone_api_key: str = os.environ["PINECONE_API_KEY"]
    pinecone_index: str = os.environ["PINECONE_INDEX"]
    pinecone_embedding_model: str = "multilingual-e5-large"
    vector_dim: int = 768


config = SectionConfig()

