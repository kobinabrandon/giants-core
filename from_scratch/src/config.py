from pathlib import Path
from pydantic_settings import SettingsConfigDict, BaseSettings
from general.paths import set_paths


class GeneralConfig(BaseSettings):
    _ = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    pad_id: int = 0
    unk_id: int = 1
    bos_id: int = 2
    eos_id: int = 3
    vocab_size: int = 14297
    spacy_max_length: int = 1400000 
    sentences_per_chunk: int = 30
    sentence_transformer_name: str = "all-mpnet-base-v2"
    batch_size_for_embedding: int = 32

    paths: dict[str, Path] = set_paths(from_scratch=True, general=False) 

config = GeneralConfig()

