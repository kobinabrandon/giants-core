import os 

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

_  = load_dotenv()


class Parameters(BaseSettings):
    _ = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    # Chunking hyperparameters
    ratio_of_tokens_in_overlap: float = 0.2
    number_of_characters_per_chunk: int = 800
    overlapping_characters_per_chunk: int = 30
    
    # Parameters of the recursive text splitter 
    add_start_index: bool = True 
    length_function: object = len
 
    # Embedding models  
    embedding_model_name: str = "thenlper/gte-large"
    pinecone_embedding_model: str = "multilingual-e5-large"
    
    # API Keys
    pinecone_api_key: str = "" #os.environ["PINECONE_API_KEY"]
    hugging_face_token: str = os.environ["HUGGING_FACE_TOKEN"]

    # Endpoints
    endpoints_under_consideration: dict[str, str] = {                           
        "wayfarer-12b-gguf-hva": os.environ["ENDPOINT_URL_OF_PREFERRED_LLM"],  # In order of preference 
        "phi-4-gguf-dej": os.environ["PHI_4_GGUF_ENDPOINT_URL"] 
    }  

    # Rejected models
    eliminated_models_with_reasons: dict[str, str] = {
        "llama-3-2-1b-mdj": "more expensive than wayfarer-12b-gguf-hva", 
        "readerlm-v2-fnd": "404 Error"
    }

config = Parameters()

