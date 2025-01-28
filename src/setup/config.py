import os

from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


env_file_present = load_dotenv(find_dotenv()) 
env_vars = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


class ChunkingSettings:
    
    # Chunking hyperparameters
    ratio_of_tokens_in_overlap: float = 0.2
    number_of_characters_per_chunk: int = 800
    overlapping_characters_per_chunk: int = 30
    
    # Parameters of the recursive text splitter 
    add_start_index: bool = True 
    length_function: object = len


class EmbedddingSettings:
    embedding_model_name: str = "thenlper/gte-large"
    pinecone_embedding_model: str = "multilingual-e5-large"
    

class Tokens(BaseSettings):

    if env_file_present:
        pinecone_api_key: str = "" #os.environ["PINECONE_API_KEY"]
        hugging_face_token: str = os.environ["HUGGING_FACE_TOKEN"]


class LLMConfig(BaseSettings):
       
    if env_file_present:
        # Endpoints
        
        url_of_preferred_llm_endpoint: str = os.environ["URL_OF_ENDPOINT_FOR_PREFERRED_LLM"] 

        endpoints_under_consideration: dict[str, str] = {                           
            "wayfarer-12b-gguf-hva": url_of_preferred_llm_endpoint, # In order of preference 
            "phi-4-gguf-dej": os.environ["PHI_4_GGUF_ENDPOINT_URL"] 
        }  

        # Rejected models
        eliminated_models_with_reasons: dict[str, str] = {
            "llama-3-2-1b-mdj": "more expensive than wayfarer-12b-gguf-hva", 
            "readerlm-v2-fnd": "404 Error"
        }


chunk_config = ChunkingSettings()
embed_config = EmbedddingSettings()
llm_config = LLMConfig()
env_config = Tokens()


