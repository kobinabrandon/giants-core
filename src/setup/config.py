from pydantic_settings import SettingsConfigDict, BaseSettings
from src.feature_pipeline.data_extraction import Book, neo_colonialism, africa_unite, dark_days


class GeneralConfig(BaseSettings):
    _ = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    pad_id: int = 0
    unk_id: int = 1
    bos_id: int = 2
    eos_id: int = 3
    spacy_max_length: int = 1400000 
    vocab_size: int = 14297

config = GeneralConfig()


def find_non_core_pages(book: Book) -> tuple[int, int]:
    
    book_and_non_core_pages = {
        neo_colonialism: (4, 201),
        africa_unite: (5, 236),
        dark_days: (7, 162)
    }

    return book_and_non_core_pages[book]

