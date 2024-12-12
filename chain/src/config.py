from pydantic_settings import BaseSettings, SettingsConfigDict


class GeneralConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    chunk_size: int = 400
    chunk_overlap: int = 100
    length_function: object = len
    add_start_index: bool = True 
    sentence_transformer_name: str = "all-mpnet-base-v2"

config = GeneralConfig()

