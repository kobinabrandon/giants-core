from pydantic_settings import SettingsConfigDict, BaseSettings
from src.feature_pipeline.data_extraction import Book, neo_colonialism, africa_unite, dark_days


class GeneralConfig(BaseSettings):
    _ = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    pad_id: int = 0
    unk_id: int = 1
    bos_id: int = 2
    eos_id: int = 3


config = GeneralConfig()



