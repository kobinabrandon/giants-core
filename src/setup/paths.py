import os 
from pathlib import Path 


PARENT_DIR = Path("__file__").parent.resolve()
DATA_DIR = PARENT_DIR / "data"
MODELS_DIR = PARENT_DIR / "models"
RAW_DATA_DIR = DATA_DIR/"raw"
CHUNK_DETAILS_DIR = DATA_DIR/"chunk_details"
NON_CORE_SECTIONS = DATA_DIR/"non_core_sections"

PAGE_DETAILS = DATA_DIR/"page_details"
PAGE_DETAILS_WITH_SPACY = PAGE_DETAILS/"with_spacy"
PAGE_DETAILS_WITHOUT_SPACY = PAGE_DETAILS/"without_spacy"

BOOK_STATS = DATA_DIR/"stats"
STATS_WITH_SPACY = BOOK_STATS/"with_spacy"
STATS_WITHOUT_SPACY = BOOK_STATS/"without_spacy"


def make_data_directories():

    for path in [
        DATA_DIR, RAW_DATA_DIR, NON_CORE_SECTIONS, CHUNK_DETAILS_DIR, MODELS_DIR, BOOK_STATS, 
        PAGE_DETAILS, PAGE_DETAILS_WITH_SPACY, PAGE_DETAILS_WITHOUT_SPACY, STATS_WITH_SPACY, 
        STATS_WITHOUT_SPACY
    ]:
        if not Path(path).exists():
            os.mkdir(path=path)
