import os 
from pathlib import Path 


def set_module_root(from_scratch: bool, general: bool) -> Path:
        
    if general:
        return Path("__file__").parent.resolve().parent.resolve() / "general"
    elif from_scratch:
        return Path("__file__").parent.resolve().parent.resolve() / "from_scratch"
    else:
        return Path("__file__").parent.resolve().parent.resolve() / "chain"


def set_paths(from_scratch: bool, general: bool) -> dict[str, Path]:
     
    MODULE_ROOT = set_module_root(from_scratch=from_scratch, general=general)
   
    DATA_DIR = MODULE_ROOT / "data"
    CLEANED_TEXT_DIR = DATA_DIR / "cleaned_text"

    paths: dict[str, Path] = {
        "data": DATA_DIR
    }

    if general:
        paths.update(
            {   
                "raw_data": DATA_DIR / "raw"
            }

        )
    
    elif from_scratch:
        MODELS_DIR = MODULE_ROOT / "models"
        BOOK_STATS = DATA_DIR / "book_stats"
        PAGE_DETAILS_DIR = DATA_DIR/"page_details"

        paths.update(
            {   
                "models": MODELS_DIR,
                "book_stats": BOOK_STATS,
                "page_details": PAGE_DETAILS_DIR,
                "chunk_details": DATA_DIR / "chunk_details",
                "non_core_sections": DATA_DIR / "non_core_sections",
                "book_stats_with_spacy": BOOK_STATS / "with_spacy",
                "book_stats_without_spacy" :BOOK_STATS / "without_spacy",
                "page_details_with_spacy": PAGE_DETAILS_DIR / "with_spacy",
                "page_details_without_spacy": PAGE_DETAILS_DIR / "without_spacy"
            } 
        )
    
    else:
        CHROMA_DIR = MODULE_ROOT / "chroma_langchain_db"
        
        paths.update(
            {"chroma": CHROMA_DIR}
        )

    paths.update(
        {
            "embeddings": DATA_DIR / "embeddings",
            "cleaned_text": CLEANED_TEXT_DIR
        }
    )

    return paths


def make_data_directories(from_scratch: bool, general: bool) -> None: 
    """

    Args:
        from_scratch: 
        general: 
    """
    paths = set_paths(from_scratch=from_scratch, general=general)
    for path in paths.values():
        if not Path(path).exists():
            os.mkdir(path=path)
    
