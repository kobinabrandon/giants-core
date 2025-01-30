import os 
from pathlib import Path 


def set_paths() -> dict[str, Path]:
     
    MODULE_ROOT = Path("__file__").parent.resolve()
   
    DATA_DIR = MODULE_ROOT / "data"
    CLEANED_TEXT_DIR = DATA_DIR / "cleaned_text"
    MODELS_DIR = MODULE_ROOT / "models"
    BOOK_STATS = DATA_DIR / "book_stats"
    PAGE_DETAILS_DIR = DATA_DIR/"page_details"
    CHROMA_DIR = MODULE_ROOT / "./chroma"

    paths: dict[str, Path] = {
        "data": DATA_DIR,
        "raw_data": DATA_DIR / "raw",
        "models": MODELS_DIR,
        "book_stats": BOOK_STATS,
        "page_details": PAGE_DETAILS_DIR,
        "cleaned_text": CLEANED_TEXT_DIR,
        "chunk_details": DATA_DIR / "chunk_details",
        "chroma_memory": CHROMA_DIR / "chroma_memory",
        "text_embeddings": CHROMA_DIR / "text_embeddings",
        "non_core_sections": DATA_DIR / "non_core_sections",
        "book_stats_with_spacy": BOOK_STATS / "with_spacy",
        "book_stats_without_spacy" :BOOK_STATS / "without_spacy",
        "page_details_with_spacy": PAGE_DETAILS_DIR / "with_spacy",
        "page_details_without_spacy": PAGE_DETAILS_DIR / "without_spacy"
    }
        
    return paths


def make_data_directories() -> None: 

    paths = set_paths()
    for path in paths.values():
        if not Path(path).exists():
            os.mkdir(path=path)
    
