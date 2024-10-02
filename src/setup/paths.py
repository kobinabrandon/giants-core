import os 
from pathlib import Path 


PARENT_DIR = Path("__file__").parent.resolve()
DATA_DIR = PARENT_DIR / "data"
RAW_DATA_DIR = DATA_DIR/"raw"

PAGE_DETAILS = DATA_DIR/"page_details"
PAGE_DETAILS_WITH_SPACY = PAGE_DETAILS/"with_spacy"
PAGE_DETAILS_WITHOUT_SPACY = PAGE_DETAILS/"without_spacy"

BOOK_STATISTICS = DATA_DIR/"statistics"
STATISTICS_WITH_SPACY = BOOK_STATISTICS/"with_spacy"
STATISTICS_WITHOUT_SPACY = BOOK_STATISTICS/"without_spacy"

def make_fundamental_paths():

    for path in [
        DATA_DIR, RAW_DATA_DIR, BOOK_STATISTICS, PAGE_DETAILS, PAGE_DETAILS_WITH_SPACY, PAGE_DETAILS_WITHOUT_SPACY, \
        STATISTICS_WITH_SPACY, STATISTICS_WITHOUT_SPACY
    ]:
        if not Path(path).exists():
            os.mkdir(path=path)