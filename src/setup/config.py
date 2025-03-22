import os
from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


env_file_present: bool = load_dotenv(find_dotenv()) 
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
    

class GroqConfig(BaseSettings):

    assert env_file_present
    preferred_model: str = "llama-3.3-70b-versatile" 
    api_key: str = os.environ["GROQ_API_KEY"]


class FrontendConfig:
    bot_name: str = "Historian" 


class VideoConfig(BaseSettings):
    feared_by_the_west: str = "https://www.youtube.com/watch?v=AgE30BXdKVY"
    why_he_was_a_threat: str = "https://www.youtube.com/watch?v=uUkYDavkm40&pp=ygUHbmtydW1haA%3D%3D" 
    untold_story: str = "https://www.youtube.com/watch?v=NKkGJk1v6os&pp=ygUHbmtydW1haA%3D%3D"
    how_he_was_overthrown: str = "https://www.youtube.com/watch?v=Wjmg9K95QoU" 
    speech_on_the_traitors: str = "https://www.youtube.com/watch?v=2niDtrZalWc" 
    halted_progress: str = "https://www.youtube.com/watch?v=o0tRJfkpe2M"
    speech_after_overthrow: str = "https://www.youtube.com/watch?v=GDtMvpDrXcY" 


chunk_config = ChunkingSettings()
embed_config = EmbedddingSettings()
frontend_config = FrontendConfig()
groq_config = GroqConfig()
videos = VideoConfig()

